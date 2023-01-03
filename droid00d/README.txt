This system is designed around the Badger 2040 device from Pimoroni.
https://github.com/pimoroni

Standard Development Setup

    1. Plug the Badger 2040 into your computer. The Badger connects via USB C, but you can connect it to a USB A or USB C connection with an appropriate cable.

    2. Install the Thonny integrated development environment from thonny.com

    Note: the device (backend) can be restarted using Ctrl-F2 if the attached device isn't recognized.

    3. In Thonny, verify the device firmware is v1.19 or newer (e.g., pimoroni-badger2040-v1.19.10-micropython.uf2)

        To load new firmware onto the Badger 2040, follow these instructions:

            a. On the back of the Badger 2040 are two buttons - BOOT/USR and RST. Hold down the BOOT/USR button and at the same time press and release the RST button, then release the BOOT/USR button. This tells the onboard RP2040 to reset and start the bootloader.

            b. Once in bootloader mode, the RP2040 device should appear as an external mass storage device on your computer.

            c. Copy the uf2 file for the firmware you wish to apply, to the RP2040 device.

            d. Once the copy is complete, the RP2040 device should automatically reset. The device will no longer appear as a mass storage device, and the Badger 2040 will now be running with the firmware you applied.

        Similar setup information references:
            https://www.thoughtasylum.com/2022/04/29/the-badger-2040-set-up/
            https://learn.pimoroni.com/article/getting-started-with-badger-2040

Standard Deployment Setup

    1. Unplug the Badger 2040 from your computer.

    2. Plug in the fully charged battery into the jst connector on the back of the Badger 2040.

    3. Verify that the device starts up correctly after pressing the RST button on back of Badger 2040.

    4. If you used a Lipo 3.7v battery, make sure to attach a protector to the badger2040 (e.g., https://www.thingiverse.com/thing:5271558).

Projects

    The projects/hello-world/ directory contains a self-standing program that is designed to display text and sample buttons in a main loop. To install this project:

        1. Using Thonny create a file in Badger 2040 device file system called 'main.py'

        2. Copy the contents of projects/hello-world/image/main.py into it.

        3. Press F5 to save and run the program on the device.

    The projects/flower/ directory contains a self-standing program that is designed to display a random image daily, from each subdirectory (i.e., images/a, images/b, images/c).

        1. Upload the image files in images/ into a matching directory structure on the device (i.e., image/a/, images/b/, images/c/):

            a. Use the Thonny View>Files menu item to open the Thonny File View.
            Note: the device (backend) can be restarted using Ctrl-F2 if the attached device isn't recognized.

            b. Use the Thonny File View context menu to manually create a directory called 'images' in the filesystem root.
            
            c. Use the Thonny File View context menu to manually create three directories inside the images directory, called 'a', 'b' and 'c'.

            d. Use the Thonny File View context menu to Upload any number of image (.bin) files into these new directories on the device.

        2. Replace the main.py file contents with /projects/flower/image/main.py.

        3. Press F5 to save and run the program on the device.
   
        Optionally, Upload (.bin) image files using flower/tools/convert.py. For example,

            flower\tools>pip install Pillow
            flower\tools>python convert.py --binary --rotate ..\image\images\a\image2.jpeg
            Saving to ..\image\images\a\image2.bin, 128x296
            flower\tools>

<eof>