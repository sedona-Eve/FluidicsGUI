import tkinter as tk  # You also need to import tkinter for creating the root window
from gui.application import Application
from hardware.cnc_controller import CNCController
from hardware.peristaltic_pump import PeristalticPump

if __name__ == '__main__':
    root = tk.Tk()  # Create the root window
    app = Application(master=root)  # Create an instance of the Application class
    app.load_default_protocol("default_protocol.xml")  # Load the default protocol

    # Create instances of CNCController and PeristalticPump classes
    #cnc = CNCController('COM4', 115200)  #uncomment when hardware connected 
    #pump = PeristalticPump('COM2', 9600) #uncomment when hardware connected 

    app.mainloop()  # Start the main event loop
