import neopixel
import board
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 1.0
LUMINANCE = 1
pixel.fill((LUMINANCE, LUMINANCE, LUMINANCE)) # Starting: white light

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print(secrets["name"] + " droid" + secrets["droid_id"])

# Connect to AP
from digitalio import DigitalInOut
esp32_cs = DigitalInOut(board.D10)
esp32_ready = DigitalInOut(board.D9)
esp32_reset = DigitalInOut(board.D6)
import busio
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
from adafruit_esp32spi import adafruit_esp32spi
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
requests.set_socket(socket, esp)
if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("FW: ", esp.firmware_version, "\tMAC:", [hex(i) for i in esp.MAC_address])
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print("Could not connect to AP, retrying: ", e)
        continue
pixel.fill((0, 0, LUMINANCE)) # Connected: blue light
print("Connected: ", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi, "\tIP: ", esp.pretty_ip(esp.ip_address))

def upload(sensor_name, sensor_value):
    TABLES = "https://vcgtjqigra.execute-api.us-west-2.amazonaws.com/proto/sensor_droid"
    attempts = 3  # Number of attempts to retry each request
    failure_count = 0
    response = None
    
    # Upload a new sample
    json_data = \
    {
      "droid_fk": secrets['droid_fk']
    }
    res = requests.get('http://worldclockapi.com/api/json/utc/now')
    json_data["time_ts"] = res.json()['currentDateTime']
    res.close()
    res = None
    
    json_data[sensor_name] = sensor_value
    SOIL_SENSOR = TABLES + "/" + "soil_" + sensor_name
    print("PUTing data to {0}: {1}".format(SOIL_SENSOR, json_data))
    while not response:
        try:
            response = requests.put(SOIL_SENSOR, json=json_data)
            failure_count = 0
        except AssertionError as error:
            print("Upload failed, retrying...\n", error)
            failure_count += 1
            if failure_count >= attempts:
                raise AssertionError(
                    "Failed to upload sensor data."
                ) from error
            continue
    print(response.text)
    response.close()
    response = None

# Read and report sensor data
from adafruit_seesaw.seesaw import Seesaw
import bitbangio
i2c = bitbangio.I2C(board.A1, board.A0)
ss = Seesaw(i2c, addr=0x36)

# Read sensor values and add sensor bias
touch = ss.moisture_read() + secrets["soil_moisture"]
temp = ss.get_temp() + secrets["soil_temp"]

pixel.fill((0, LUMINANCE, 0)) # Uploading: green light

upload("moisture", str(touch))
upload("temp", str(temp))

import alarm
import time
# Create a an alarm that will trigger after a specified timer elapses.
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*5)
# Exit the program, and then deep sleep until the alarm wakes us.
pixel.fill((0, 0, 0)) # Completed: no light
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
# Does not return. When the timer elapses, the program restarts.




