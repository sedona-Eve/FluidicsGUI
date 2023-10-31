'''
bugs fixed 10-30-23 Sedona Murphy 
# adapted from gilsonmp3.py by George Emanuel with modifications by Jeff Moffitt
# 11/16/15

pump class to work with cnc for portable fluidics system. 
'''

import os
import serial
import time
import subprocess
import threading

# Define communication protocol variables
acknowledge = '\x06'
start = '\x0A'
stop = '\x0D

class PeristalticPump:
    def __init__(self, port, baudrate, simulate=False, flip_flow_direction=False, pump_ID=30, serial_verbose):
        self.serial = None
        self.simulate = simulate
        self.flip_flow_direction = flip_flow_direction
        self.pump_ID = pump_ID
        
        self.serial_verbose =  True #set to false when done troubleshooting
        

        # Initialize the serial port
        try:
            self.serial = serial.Serial(port=self.com_port, 
                            baudrate=19200, 
                            parity=serial.PARITY_EVEN, 
                            bytesize=serial.EIGHTBITS, 
                            stopbits=serial.STOPBITS_TWO, 
                            timeout=0.1)
        except serial.SerialException as e:
            raise RuntimeError(f"Error: Unable to open the serial port: {e}")
            # may need to update this based on the specific one you are using.


        
    def sendBuffered(self, unitNumber, command):
        self.selectUnit(unitNumber)
        self.sendAndAcknowledge(start + command + stop)
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
        # Define a new method to stop the flow without freezing the GUI
        def stop_flow():
            self.setSpeed(0.0)
        
        # Create a new thread to run the stop_flow method
        stop_flow_thread = threading.Thread(target=stop_flow)
        
        # Start the thread
        stop_flow_thread.start()
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
