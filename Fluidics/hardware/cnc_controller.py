import os
import serial
import time
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
    
