import tkinter as tk  # You also need to import tkinter for creating the root window
from gui.application import Application
from hardware.cnc_controller import CNCController
from hardware.peristaltic_pump import PeristalticPump

if __name__ == '__main__':
    root = tk.Tk()  # Create the root window

    # Create instances of CNCController and PeristalticPump classes
    cnc = CNCController('COM4', 115200)  #uncomment when hardware connected 
    pump = PeristalticPump('COM6', 19200) #uncomment when hardware connected 
    app= Application(master=root, pump=pump, cnc=cnc)  # Create an instance of the Application class, a
    app.load_default_protocol("default_protocol.xml")  # Load the default protocol 

    app.mainloop()  # Start the main event loop
