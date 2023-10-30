import os
import serial
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import xml.etree.ElementTree as ET
import subprocess


class Application(tk.Frame):
    def __init__(self, master=None, cnc=None, pump=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.master.title("Hybridization Station")
        self.master.geometry("1800x500")
        self.master.configure(bg='#ADD8E6')  # set background color
        #self.cnc = cnc  #
        self.pump = pump #
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

	self.pause_duration_label = tk.Label(self, text="Pause Duration (sec):", font=label_font)
	self.pause_duration_label.grid(row=7, column=13, sticky="E")
	self.pause_duration_entry = tk.Entry(self, font=label_font)
	self.pause_duration_entry.grid(row=7, column=14, sticky="W", pady=5)

	self.pause_button = tk.Button(
    	    self,
    	    text="Pause",
    	    font=button_font,
    	    padx=5,
   	    pady=5,
    	    command=self.pause_action,
	)
	self.pause_button.grid(row=8, column=13, pady=5)

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
        print("starting Flow...")
        speed = float(self.flow_rate_entry.get())
        duration = float(self.flow_duration_entry.get())
        print(f"Speed: {speed}, Duration: {duration}")
        self.pump.startFlow(speed, duration)
    
    def stop_flow(self):
        self.pump.stopFlow()
	    
    def pause_action(self, pause_duration):
    	try:
        	pause_duration = float(self.pause_duration_entry.get())
    	except ValueError:
        	messagebox.showerror("Error", "Invalid pause duration. Please enter a valid number.")
        	return

    	print(f"Pausing for {pause_duration} seconds...")
    	time.sleep(pause_duration)
    	print("Pause complete.")


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
	    self.steps = self.loaded_steps  # Use the loaded_steps list for execution
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
                            self.dispense(action_attributes["buffer"])
                    elif action_name == "pump":
                        self.startFlow(
                            action_attributes["name"],
                           float( action_attributes["speed"]),
                            float(action_attributes["time"]),
                        )
                    elif action_name == "pause":
			pause_duration = action_attributes.get("time")
			self.pause_action(float(pause_duration))  # Convert to float if necessary

                        

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
    	
    


