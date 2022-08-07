This system is designed for monitoring (e.g., sunlight, temperature, humidity, soil moisture) within range of an access point (WiFi)

1. LiPo battery 3.7v (e.g., three cell 6600+ mAh)
2. USB-C RP2040 micro-controller, w/ MicroPython I2C & SPI support
3. NeoPixel
4. Soil moisture sensor w/ on board soil temp sensor
5. UV sensor
6. Humidity sensor
7. AirLift Wifi breakout

Development System Setup

1. Hold BootSel button and plug-in as USB drive mounted as RPI-RP2.
2. Download the latest CircuitPython .uf2 bootloader (e.g., 7.3.2), and drag to the USB drive. Once it is finished it should automatically remount as CIRCUITPY.
3. Copy the latest code.py to CIRCUITPY, replacing the default code.py script.
4. Copy the latest secrets.py to the root of CIRCUITPY. Then edit the copy and specify your local access point (SSID) and password, etc.
5. Download the https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20220727/adafruit-circuitpython-bundle-7.x-mpy-20220727.zip file, unzip it, and copy over the subfolders, such as lib, into the root of your CIRCUITPY device.
6. "Eject" the CIRCUITPY (USB) device (e.g., Rt-Click on the device in the file explorer).
7. Use Device Manager to determine which COM port the device is exposed as.
8. Use Putty (or other terminal emulator) to attach to the COM port at baud rate 115200.
9. Press CTRL-D to restart/reboot the device and run the startup script (code.py).
