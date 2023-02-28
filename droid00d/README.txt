This system is designed around the Badger 2040 device from Pimoroni.
https://github.com/pimoroni

Standard Development Setup

    1. Plug the Badger 2040 into your computer. The Badger connects via USB C, but you can connect it to a USB A or USB C connection with an appropriate cable.

    2. Install the Thonny integrated development environment from thonny.com

    Note: the device (backend) can be restarted using Ctrl-F2 if the attached device isn't recognized.

    3. In Thonny, verify the device firmware is v1.19 or newer (e.g., pimoroni-badger2040-v1.19.10-micropython.uf2). The latest release can be found here: https://github.com/pimoroni/pimoroni-pico/releases

        To load new firmware onto the Badger 2040, follow these instructions:

            a. On the back of the Badger 2040 are two buttons - BOOT/USR and RST. Hold the BOOT/USR button while triggering the RST. This tells the onboard RP2040 to restart in the mountable storage device mode and appear as an external mass storage device on your computer.

            b. Copy the uf2 file for the firmware you wish to apply, to the RP2040 device. Once the copy is complete, the RP2040 device should automatically reset. The device will no longer appear as a mass storage device, and the Badger 2040 will now be running with the firmware you applied.

        Similar setup information references:
        
            https://www.thoughtasylum.com/2022/04/29/the-badger-2040-set-up/
            https://learn.pimoroni.com/article/getting-started-with-badger-2040

Standard Deployment Setup

    1. Unplug the Badger 2040 from your computer.

    2. Plug in the fully charged battery into the jst connector on the back of the Badger 2040.

    3. Verify that the device starts up correctly after pressing the RST button on back of Badger 2040.

    4. If you used a Lipo 3.7v battery, make sure to attach a protector to the badger2040 (e.g., https://www.thingiverse.com/thing:5271558).

Projects

    The hello-world/ directory contains a self-standing program that is designed to display text and sample buttons in a main loop. To install this project:

        1. Once connected, open the 'main.py' file on the root of the RP2040 device.

        2. Replace the contents of this file with that of hello-world/image/main.py.

        3. Press F5 to save and run the program on the device.

    The flower/ directory contains a self-standing program that is designed to display a random image daily, from each subdirectory of images.

        1. Upload the image files in image/ into a matching directory structure on the device (i.e., top/, middle/, bottom/):

            a. Enable the Thonny Files pane using the View>File menu item.
            Note: If needed, the device (backend) can be restarted using Ctrl-F2 if the attached device isn't recognized in which case you may not see the My Computer or RP2040 Device selection dialog which precedes the standard file selection dialog. You can optionally also remove other files if they exist.

            b. Use the Thonny File View context menu to manually create a directory called 'images' in the filesystem root. You can optionally remove other directories if they exist.
            
            c. Use the Thonny File View context menu to manually create three directories inside the images directory, called 'top', 'middle' and 'bottom'.

            d. Use the Thonny File View selection mechanism to navigate into each of these subdirectories, and then use the context menu to Upload any number of image (.bin) files the My Computer into these new directories on the device.

        2. Replace the main.py file contents with flower/image/main.py.

        3. Press F5 to save and run the program on the device.
   
        Optionally, Upload additional/new (.bin) image files after using flower/tools/convert.py, for example:
            If needed, install Python and PIP, the package installer for Python.
            If needed, run flower\tools>pip install Pillow
            Run 'python convert.py --binary --rotate <file>'       
<eof>
