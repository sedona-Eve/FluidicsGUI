'''
Fluidics GUI to automate handling of buffers and hybridizations during sequential imaging experiments. 

see "readme" file for details 

need: cnc_coords.xml file defining the x,y,z of 96 well plate and buffer reservoirs 
default_protocol.xml withe default 96 hybridizations 
optional: load your own .xml protocol file 

set the COM ports and baudrates of cnc and pump and uncomment before running 

Sedona Murphy 
2023-05-22

'''
import os
import serial
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import xml.etree.ElementTree as ET
import subprocess



class CNCController:
    def __init__(self, port, baudrate):
        ##you need to update these for your specific device        
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.goToPointOfOrigin()
        
    def goToPointOfOrigin(self):
        # Set the specified position as the origin using absolute positioning
        self.sendCommand("$H\n")    #Homing device at the beginning of the experiment
        self.sendCommand("G21 G90 G94\n")#sets machine in mm (G21) and allows feedrate code (G94)
        self.sendCommand("G92 X0 Y0 Z0\n") #sets starting coordinates to 0

        
        time.sleep(1)  # Pause for 1 second

    def sendCommand(self, cmd):
        self.ser.write(cmd.encode())
        response = self.ser.readline()
        return response
        
    def moveUp(self, distance):
        # Send commands to move the CNC router up by the specified distance
        self.sendCommand(f"G01 Z{distance}\n")
        time.sleep(1)  # Pause for 1 second

    def moveDown(self, distance):
        # Send commands to move the CNC router down by the specified distance
        self.sendCommand(f"G01 Z-{distance}\n")
        time.sleep(1)  # Pause for 1 second

    def moveToPosition(self, x, y, z, well_name):
    #interprets the gcode of the cnc router
        # Move up before going to the well
        self.moveUp(0)   #update this depending on needle height and well height 
        time.sleep(1)  # Pause for 1 second in between moves

        # Move to the specified position (x, y, z) for the well
        self.sendCommand(f"G01 F1000.0 X{x} Y{y}\n") #change speed with F
        self.sendCommand(f"G01 F1000.0 Z{z}\n")
        time.sleep(1)  # Pause for 1 second

        # Move out of the well by a small distance
        #self.sendCommand("G01 X10 Y10\n")
        #time.sleep(1)  # Pause for 1 second

        # Move down into the well. This function can be used instead of defining z in coordinates
        #self.moveDown(-30)  #update this depending on needle and well height
        #time.sleep(1)  # Pause for 1 second
    



class PeristalticPump:
    def __init__(self, port, baudrate, simulate=False, flip_flow_direction=False, pump_ID=30):
        self.serial = None
        self.simulate = simulate
        self.flip_flow_direction = flip_flow_direction
        self.pump_ID = pump_ID

        # Initialize the serial port
        try:
            self.serial = serial.Serial(port=self.com_port, 
                            baudrate=19200, 
                            parity=serial.PARITY_EVEN, 
                            bytesize=serial.EIGHTBITS, 
                            stopbits=serial.STOPBITS_TWO, 
                            timeout=0.1)
        except serial.SerialException:
            print("Error: Unable to open the serial port. Check the port and baudrate.")
            # may need to update this based on the specific one you are using.

        # Define communication protocol variables
        self.acknowledge = '\x06'
        self.start = '\x0A'
        self.stop = '\x0D'
        
    def sendBuffered(self, unitNumber, command):
        self.selectUnit(unitNumber)
        self.sendAndAcknowledge(self.start + command + self.stop)
        self.disconnect()

    def sendString(self, string):
        if self.serial:
            self.serial.write(string.encode())

    def getResponse(self):
        response = b""
        if self.serial:
            while True:
                data = self.serial.read(1)
                if not data:
                    break
                response += data
        return response

    def getIdentification(self):
        return self.sendImmediate(self.pump_ID, "%")

    def enableRemoteControl(self, remote):
        if remote:
            self.sendBuffered(self.pump_ID, "SR")
        else:
            self.sendBuffered(self.pump_ID, "SK")

    def getStatus(self):
        message = self.readDisplay()

        if self.flip_flow_direction:
            direction = {" ": "Not Running", "-": "Forward", "+": "Reverse"}.get(message[0], "Unknown")
        else:
            direction = {" ": "Not Running", "+": "Forward", "-": "Reverse"}.get(message[0], "Unknown")

        status = "Stopped" if direction == "Not Running" else "Flowing"

        control = {"K": "Keypad", "R": "Remote"}.get(message[-1], "Unknown")

        auto_start = "Disabled"

        speed = float(message[1:len(message) - 1])

        return (status, speed, direction, control, auto_start, "No Error")

    def close(self):
        self.enableRemoteControl(0)

    def setFlowDirection(self, forward):
        if self.flip_flow_direction:
            if forward:
                self.sendBuffered(self.pump_ID, "K<")
            else:
                self.sendBuffered(self.pump_ID, "K>")
        else:
            if forward:
                self.sendBuffered(self.pump_ID, "K>")
            else:
                self.sendBuffered(self.pump_ID, "K<")
                

    def setSpeed(self, rotation_speed):
        if rotation_speed >= 0 and rotation_speed <= 48:
            rotation_int = int(rotation_speed * 100)
            self.sendBuffered(self.pump_ID, f"R{rotation_int:04d}")

    def startFlow(self, speed, duration, direction="Forward"):
        self.setSpeed(speed)
        self.setFlowDirection(direction == "Forward")
        time.sleep(duration)  # Wait for the specified duration
        self.stopFlow()  # Stop the flow after the duration

    def stopFlow(self):
        self.setSpeed(0.0)
        return True


    def readDisplay(self):
            # Send the "R" command to request the display status
            response = self.sendImmediate(self.pump_ID, "R")

            if not response:  # Check if response is an empty string
                print('Error: No response received from the pump!')
                return None

            # The response format is "dXX.XXca"
            direction_char = response[1]
            speed_str = response[2:7]
            control_char = response[7]

            # Interpret the direction character
            direction = ""
            if direction_char == " ":
                direction = "Not Running"
            elif direction_char == "+":
                direction = "Forward"
            elif direction_char == "-":
                direction = "Reverse"

            # Convert the speed string to a floating-point value
            speed = float(speed_str)

            # Interpret the control character
            control = ""
            if control_char == "K":
                control = "Keypad"
            elif control_char == "R":
                control = "Remote"

            return direction, speed, control


    def sendImmediate(self, unitNumber, command):
        self.selectUnit(unitNumber)
        self.sendString(command[0])
        newCharacter = self.getResponse()
    
        if not newCharacter:  # Check if newCharacter is an empty string
            print('Error: No response received from the pump!')
            self.disconnect()
            return None

        response = ""
        while not (ord(newCharacter) & 0x80):
            response += newCharacter.decode()
            self.sendString(self.acknowledge)
            newCharacter = self.getResponse()

            if not newCharacter:  # Check if newCharacter is an empty string
                print('Error: No response received from the pump!')
                self.disconnect()
                return None

        response += chr(ord(newCharacter) & ~0x80)
        self.disconnect()

        return response


    def disconnect(self):
        self.sendAndAcknowledge('\xff')

    def selectUnit(self, unitNumber):
        devSelect = chr(0x80 | unitNumber)
        self.sendString(devSelect) 

        return self.getResponse() == devSelect

    def sendAndAcknowledge(self, string):
        for i in range(0, len(string)):
            self.sendString(string[i])
            self.getResponse()




class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.master.title("Hybridization Station")
        self.master.geometry("1800x500")
        self.master.configure(bg='#ADD8E6')  # set background color
        self.cnc = CNCController('COM4', 115200)  #update this for your device, uncomment and add COM port and baudrate (number)
        self.pump = PeristalticPump('COM2', 9600)  #update this for your device, uncomment and add COM portand baudrate (number)
        self.positions = self.loadPositions("CncCoords.xml")  #update this for your device
        self.protocol_file= None
        self.steps=[]
        self.current_step= 0
        self.total_step=0
        self.load_default_protocol("default_protocol.xml") 
        #self.button_font = ("Helvetica", 10, "bold")  # Define button_font as an instance variable
        self.configure_gui()
       
    def create_widgets(self):
        # Create a font for the buttons and labels
        button_font=("Helvetica", 12)
        label_font = ("Helvetica", 12)

        # Creates all of the buttons on the GUI
        self.move_to_well_buttons = []
        for i in range(1, 97):
            well_name = f"Hybridize {i}"
            button = tk.Button(
                self,
                text=well_name,
                font=button_font,
                padx=5,
                pady=5,
                bg='#ADD8E6',  # set background color
                command=lambda well_name=well_name: self.move_to_well(well_name),
            )
            button.grid(row=(i - 1) // 12 + 2, column=(i - 1) % 12, padx=2, pady=2)
            self.move_to_well_buttons.append(button)

        # Create dropdown menu for hybridization selection
        self.hybridization_label = tk.Label(self, text="Plate:", font=label_font)
        self.hybridization_label.grid(row=1, column=0, sticky="E")
        self.hybridization_options = [f"Hybridization {i}" for i in range(1, 97)]
        self.hybridization_selection = tk.StringVar()
        self.hybridization_selection.set(self.hybridization_options[0])
        self.hybridization_option_menu = tk.OptionMenu(
            self, self.hybridization_selection, *self.hybridization_options
        )
        self.hybridization_option_menu.config(font=button_font, padx=5, pady=5)
        self.hybridization_option_menu.grid(row=9, column=14, sticky="W")

        self.select_buffer_label = tk.Label(self, text="Select Buffer:", font=label_font)
        self.select_buffer_label.grid(row=0, column=13, sticky="E")
        self.buffer_selection = tk.StringVar()
        self.buffer_selection.set("Imaging")
        self.buffer_options = ["Bleach", "Imaging", "Wash"]
        self.buffer_option_menu = tk.OptionMenu(
            self, self.buffer_selection, *self.buffer_options
        )
        self.buffer_option_menu.config(font=button_font, padx=5, pady=5)
        self.buffer_option_menu.grid(row=0, column=14, sticky="W")

        self.dispense_button = tk.Button(
            self, text="Move to Buffer", font=button_font, command=lambda well_name=well_name: self.dispense(well_name),
        )
        self.dispense_button.grid(row=1, column=14, pady=5)

        self.flow_rate_label = tk.Label(self, text="Flow Rate (ml/min):", font=label_font)
        self.flow_rate_label.grid(row=2, column=13, sticky="E")

        self.flow_rate_entry = tk.Entry(self, font=label_font)
        self.flow_rate_entry.grid(row=2, column=14, sticky="W", pady=5)

        self.flow_duration_label = tk.Label(
            self, text="Flow Duration (sec):", font=label_font
        )
        self.flow_duration_label.grid(row=3, column=13, sticky="E")
        self.flow_duration_entry = tk.Entry(self, font=label_font)
        self.flow_duration_entry.grid(row=3, column=14, sticky="W", pady=5)

        self.start_flow_button = tk.Button(
            self,
            text="Start Flow",
            font=button_font,
            padx=5,
            pady=5,
            command=self.start_flow,
        )
        self.start_flow_button.grid(row=4, column=13, pady=5)

        self.stop_flow_button = tk.Button(
            self,
            text="Stop Flow",
            font=button_font,
            padx=5,
            pady=5,
            command=self.stop_flow,
        )
        self.stop_flow_button.grid(row=4, column=14, pady=5)

        self.load_protocol_button = tk.Button(
            self,
            text="Load Protocol",
            font=button_font,
            padx=5,
            pady=5,
            command=self.load_protocol,
        )
        self.load_protocol_button.grid(row=8, column=13, pady=5)

        self.start_protocol_button = tk.Button(
            self,
            text="Start Protocol",
            command=self.start_protocol,
            state="disabled",
            bg="green",
            fg="white",
            font=("Arial", 12),
        )
        self.start_protocol_button.grid(row=5, column=14)

        self.stop_protocol_button = tk.Button(
            self,
            text="Stop Protocol",
            command=self.stop_protocol,
            state="disabled",
            bg="red",
            fg="white",
            font=("Arial", 12),
        )
        self.stop_protocol_button.grid(row=5, column=13)

        self.status_label = tk.Label(
            self,
            text="Status: N/A",
            font=("Arial", 12),
            fg="blue"
        )
        self.status_label.grid(row=6, column=14, columnspan=10)

        self.show_status_button = tk.Button(
            self,
            text="Show Status",
            command=self.show_status,
            bg="orange",
            fg="blue",
            font=("Arial", 12),
        )
        self.show_status_button.grid(row=6, column=13)

        self.grid()


        self.open_gui_button = tk.Button(
            self,
            text="Open Protocol setup",
            font=button_font,
            padx=5,
            pady=5,
            command=self.open_another_gui,
        )
        self.open_gui_button.grid(row=7, column=13)

    def open_another_gui(self):
        subprocess.Popen(["python", "Define_Protocol.py"])  # Replace "another_gui_script.py" with the actual filename of your another GUI script


    def configure_gui(self):
        # Apply some basic styling to the GUI
        self.configure(bg="white")  # Set background color
        self.option_add("*Font", "Helvetica")  # Set default font
        self.option_add("*Button.Background", "#ADD8E6")  # Set button background color
        #self.option_add("*Button.Font", self.button_font)  # Set button font
        #self.option_add("*Label.Font", label_font)  # Set label font

    def loadPositions(self, filename):
    #make sure the cncCoords.xml file is in the same folder as the GUI and it will auto populate coords
        positions = {}
        
        tree = ET.parse(filename)
        root = tree.getroot()
        for child in root:
            name = child.attrib["name"]
            positions[name] = {}
            positions[name]["x"] = float(child.attrib["x"])
            positions[name]["y"] = float(child.attrib["y"])
            positions[name]["z"] = float(child.attrib["z"])
        print(positions)
        return positions    
   
    def move_to_well(self, well_name):
        print("moving to well:", well_name)
       #well_name = self.buffer_selection.get()
        x = self.positions[well_name]["x"]
        y = self.positions[well_name]["y"]
        z = self.positions[well_name]["z"]
        self.cnc.moveToPosition(x, y, z, well_name)
       
    def dispense(self, well_name):        
        well_name = self.buffer_selection.get()
        print("moving to well:", well_name)
        x = self.positions[well_name]["x"]
        y = self.positions[well_name]["y"]
        z = self.positions[well_name]["z"]
        self.cnc.moveToPosition(x, y, z, well_name)

    def start_flow(self):
        speed = float(self.flow_rate_entry.get())
        duration = float(self.flow_duration_entry.get())
        self.pump.startFlow(speed, duration)
    
    def stop_flow(self):
        self.pump.stopFlow()



    def load_default_protocol(self, default_protocol_path):
    #autoloads the default_protocol.xml for 1-96 hybridizations 
        # Parse the XML file and extract the steps
        tree = ET.parse(default_protocol_path)
        root = tree.getroot()

        self.default_steps = []

        for step in root.findall("step"):
            step_name = step.attrib["name"]
            actions = []

            for action in step:
                action_name = action.tag
                action_attributes = action.attrib
                actions.append((action_name, action_attributes))

            self.default_steps.append((step_name, actions))

        #print(self.default_steps)

        # Enable the Load and Start buttons
        self.load_protocol_button.configure(state="normal")
        self.start_protocol_button.configure(state="normal")
        self.stop_protocol_button.configure(state="normal")

    def load_protocol(self):
        file_path = filedialog.askopenfilename(
            title="Select Protocol", filetypes=(("XML files", "*.xml"),)
        )
        if not file_path:
            return

        # Parse the XML file and extract the steps
        tree = ET.parse(file_path)
        root = tree.getroot()

        self.loaded_steps = []

        for step in root.findall("step"):
            step_name = step.attrib["name"]
            actions = []

            for action in step:
                action_name = action.tag
                action_attributes = action.attrib
                actions.append((action_name, action_attributes))

            self.loaded_steps.append((step_name, actions))

        #print(self.loaded_steps)

        # Enable the Start and Pause buttons
        self.start_protocol_button.configure(state="normal")
        self.stop_protocol_button.configure(state="normal")

    def start_protocol(self):
        # Disable the Load and Start buttons
        self.load_protocol_button.configure(state="disabled")
        self.start_protocol_button.configure(state="disabled")
        self.stop_protocol_button.configure(state="normal")
        self.current_step = 0

        if self.protocol_file:
            # Load protocol from the user-defined file
            self.load_protocol_from_file(self.protocol_file)
        else:
            # Get the selected hybridization from the dropdown menu
            selected_hybridization = self.hybridization_selection.get()
            hybridization_number = int(selected_hybridization.split()[-1])

            # Find the corresponding step in the default protocol
            step_name = f"Hybridization {hybridization_number}"
            selected_step = None

            for step in self.default_steps:
                if step[0] == step_name:
                    selected_step = step
                    break

            if selected_step is None:
                print("Error: Selected hybridization not found in the default protocol.")
                return

            # Update the steps list with the selected step
            self.steps = [selected_step]
            self.total_steps = 1

        # Execute the steps in the protocol
        for step in self.steps:
            # Process default steps
            if step in self.default_steps:
                for action in step[1]:
                    action_name = action[0]
                    action_attributes = action[1]

                    if action_name == "move":
                        if "well" in action_attributes:
                            self.move_to_well(action_attributes["well"])
                        elif "buffer" in action_attributes:
                            self.move_to_buffer(action_attributes["buffer"])
                    elif action_name == "pump":
                        self.startFlow(
                            action_attributes["name"],
                           float( action_attributes["speed"]),
                            float(action_attributes["time"]),
                        )
                    elif action_name == "pause":
                        self.pause(action_attributes["time"])

            # Process loaded steps
            if step in self.loaded_steps:
                for action in step[1]:
                    action_name = action[0]
                    action_attributes = action[1]

                    # Process the loaded steps based on their actions

        # Re-enable the Load and Start buttons
        self.load_protocol_button.configure(state="normal")
        self.start_protocol_button.configure(state="normal")
        self.stop_protocol_button.configure(state="disabled")
        self.status_label.config(text="Status: Protocol finished")


		
    def stop_protocol(self):
    	self.protocol_running = False
    	self.current_step.set("Protocol stopped")
    	self.current_step_label.update()
    	for pump in self.pumps:
    		pump.stop_flow()
    	self.current_well = None
    	self.current_buffer = None
    	self.current_step_num = None
    	self.start_protocol_button.configure(state="normal")
    	self.stop_protocol_button.configure(state="disabled")
		
    def update_status_label(self):
    	if self.current_step < self.total_steps:
    		step = self.steps[self.current_step]
    		step_name = step[0]
    		time_remaining = self.get_time_remaining(step[1])
    		status_text = f"Status: {step_name} - {time_remaining}s remaining"
    		self.status_label.config(text=status_text)
    	else:
    		self.status_label.config(text="Status: Protocol finished")
    def show_status(self):
    	status = f"Step {self.current_step+1}/{self.total_steps}"
    	self.status_label.config(text=f"Status: {status}")  
    
		
    def protocol_loop(self):
    	self.protocol_running = True
    	while self.protocol_running:
    		self.update_status_label()
    		self.root.update()
    		time.sleep(0.1)
    	self.update_status_label()
    	
    



        
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.load_default_protocol("default_protocol.xml")
    app.mainloop()
