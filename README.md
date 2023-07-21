# FluidicsGUI
Instructions and python code for automated fluidics system to run multiple rounds of hybridization


Materials:
Cnc router:
https://www.amazon.com/SainSmart-Genmitsu-3018-PROVer-Switches-Emergency-Stop/dp/B07ZFD6SKP/ref=sr_1_23?keywords=cnc+router&qid=1683221624&sr=8-23

Gilson pump:
https://www.gilson.com/default/shop-products/benchtop-devices/peristaltic-pumps.html

Usb-to-serial cable: 
https://www.amazon.com/s?k=usb+to+db9+male+serial+adapter&i=electronics&hvadid=409916335620&hvdev=c&hvlocphy=9031970&hvnetw=g&hvqmt=e&hvrand=7264615173020594119&hvtargid=kwd-24272825388&hydadcr=18062_11398739&tag=googhydr-20&ref=pd_sl_7ekdthodn4_e



Instructions for connecting the hardware:
***update the COM ports and baud rates in the GUI code***
To connect the SainSmart CNC router to your computer, you will need a USB cable that connects the CNC router to your computer's USB port. 

Plug usb cord to computer and cnc
.Turn on the CNC router and wait for it to initialize.
Download and install the SainSmart CNC Controller software from the SainSmart website.
Launch the SainSmart CNC Controller software and connect to the CNC router using the USB port.
Configure the CNC router settings in the software to match your specific router.
Once the CNC router is connected to your computer and configured in the software, you can use the GUI to control the router's movements and send G-code commands to the router to perform specific tasks.

To connect a Gilson peristaltic pump to a Windows computer:
 you will need a USB-to-serial converter cable to connect the pump to the computer's USB port. The Gilson pump uses a standard RS-232 serial connection, so you will need a cable that has a DB9 serial connector on one end and a USB connector on the other end.

1.Plug the USB end of the converter cable into an available USB port on your computer.

2. Plug the DB9 end of the converter cable into the RS-232 port on the back of the Gilson pump.

3. Open the Device Manager on your Windows computer by typing "Device Manager" in the search box on the taskbar.

4. Expand the "Ports (COM & LPT)" section in the Device Manager to see the available serial ports.

5. Note the COM port number assigned to the USB-to-serial converter cable. You will need this information when configuring the pump in the GUI.

Now that the pump is connected to the computer, you can configure the GUI to communicate with the pump by selecting the correct COM port and baud rate in the pump control settings.

Instructions for making the python environment:
 
1. Install Python: If you don't have Python installed on your computer, download and install the latest version from the official Python website (https://www.python.org/downloads/). Choose the appropriate version for your operating system.

2. Install a package manager: Python has several package managers that make it easy to install and manage third-party packages. Two popular package managers are pip and conda. You can choose either one, depending on your preference.

3. Create a virtual environment: A virtual environment is a self-contained Python environment that allows you to install packages without affecting the global Python environment. To create a virtual environment, open a terminal or command prompt and navigate to a directory where you want to create the environment. Then run the following command:


   ```
pip install virtualenv
   python -m venv myenv
   ```

   This command creates a new virtual environment named "myenv" in the current directory.

4. Activate the virtual environment: To use the virtual environment, you need to activate it. Run the following command:


   ```
   source myenv/bin/activate  # for Linux and macOS
   myenv\Scripts\activate.bat  # for Windows
   ```

   This command activates the "myenv" environment.

5. Install the required packages: To run the GUI, you will need to install several packages, such as PyQt5, pyserial, lxml, pillow, numpy. To install these packages, run the following command:

   ```
   pip install PyQt5 pyserial
   ```

   This command installs PyQt5 and pyserial packages.

6. Clone the repository: Clone the repository that contains the GUI code and navigate to its directory.

7. Run the GUI: To run the GUI, run the following command:

   ```
   python HybridizationStationGUI.py
   ```

   This command starts the GUI.


If you want to launch the GUI from a shortcut on your desktop (windows):

1. Right-click on an empty space on your desktop and select "New" and then "Shortcut".

2. In the "Create Shortcut" window, enter the following information:

   - Type the location of the item: [The full path to your Python executable followed by the full path to the main.py file, e.g. "C:\Python39\python.exe C:\Users\UserName\path\to\main.py"]
   - Type a name for this shortcut: [Choose a name for the shortcut, e.g. "My CNC GUI"]

3. Click "Next", then click "Finish".

4. You should now see the shortcut icon on your desktop. Double-click on it to launch the GUI.

Note that the exact steps may vary slightly depending on your version of Windows and the location
 of your Python executable and main.py file.


Mac (although you will likely run this from windows):

1. Open the Finder application and navigate to the directory where your Python executable and main.py file are located.

2. Right-click on the main.py file and select "Get Info" or press Command + I.

3. In the "Get Info" window, under the "General" section, find the "Where" field and highlight the full path to the main.py file.

4. Copy the highlighted path using Command + C.

5. Right-click on your desktop and select "New Folder" to create a new folder on your desktop.

6. Rename the new folder to something meaningful, like "CNC GUI".

7. Right-click on the new folder and select "Get Info" or press Command + I.

8. In the "Get Info" window, under the "Name & Extension" section, select the current name of the folder and replace it with the desired name of your shortcut, like "My CNC GUI".

9. Add the following text to the end of the name: ".app", which will make it a clickable application.

10. Open the folder and create a new file by selecting "File" and then "New Document" from the menu bar.

11. In the new document, type the following text:

```
#!/bin/bash
cd <PATH_TO_PYTHON_EXECUTABLE>
./python <PATH_TO_MAIN.PY>
```

Replace `<PATH_TO_PYTHON_EXECUTABLE>` with the full path to your Python executable and `<PATH_TO_MAIN.PY>` with the full path to your main.py file.

12. Save the file with the name "run.sh" and close the text editor.

13. Open Terminal and navigate to the directory where your "My CNC GUI.app" folder is located.

14. Type the following command in Terminal to make the "run.sh" file executable:

```
chmod +x run.sh
```

15. Drag and drop the "run.sh" file into the "My CNC GUI.app" folder.

16. Close Terminal and double-click on the "My CNC GUI.app" folder to launch the GUI.

Note that the exact steps may vary depending on your version of macOS and the location of your Python executable and main.py file.


