# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 17:25:40 2023

@author: hafnera4
"""

import serial
import time

def send_gcode_command(ser, command):
    ser.write((command + '\n').encode())
    response = ser.readline().decode().strip()
    return response

def main():
    # Replace '/dev/ttyUSB0' with the appropriate serial port for your CNC controller
    serial_port = 'COM4'
    baud_rate = 115200

    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=2)
        print("Serial connection established.")

        # Wait for a moment to allow the CNC controller to initialize
        time.sleep(2)

        # Send the homing command ($H)
        homing_command = "$H"
        response = send_gcode_command(ser, homing_command)

        # Print the response from the CNC controller
        print("Response:", response)

    except serial.SerialException as e:
        print("Serial connection error:", e)
    finally:
        if ser:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
