import neopixel
import board
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 1.0
LUMINANCE = 1
pixel.fill((LUMINANCE, LUMINANCE, LUMINANCE))

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
print("Firmware: ", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print("Could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
pixel.fill((0, 0, LUMINANCE))
print("IP lookup sensordroid.dev: %s" % esp.pretty_ip(esp.get_host_by_name("www.sensordroid.dev")))
print("Ping sensordroid.dev: %d ms" % esp.ping("www.sensordroid.dev"))

# Verify that the required DB tables exist
TABLES = "https://vcgtjqigra.execute-api.us-west-2.amazonaws.com/proto/sensor_droid"
attempts = 3  # Number of attempts to retry each request
failure_count = 0
response = None
print("Verifying DB tables using %s" % TABLES)
while not response:
    try:
        response = requests.get(TABLES)
        failure_count = 0
    except AssertionError as error:
        print("Request for tables failed, retrying...\n", error)
        failure_count += 1
        if failure_count >= attempts:
            raise AssertionError(
                "Failed to resolve hostname, please check your router's DNS configuration."
            ) from error
        continue
db_tables = response.json()
response.close()
response = None
print(db_tables)

# Determine droid fk
droid_fk = "1" # TODO

import adafruit_pcf8523
rtc = adafruit_pcf8523.PCF8523(busio.I2C(board.SCL, board.SDA))
def upload(sensor_name, sensor_value):
    attempts = 3  # Number of attempts to retry each request
    failure_count = 0
    response = None
    
    # Upload a new sample
    json_data = \
    {
      "droid_fk": droid_fk
    }
    t = rtc.datetime
    json_data["time_ts"] = str(t.tm_year) + "-" + str(t.tm_mon) + "-" + str(t.tm_mday) + " " + str(t.tm_hour) + ":" + str(t.tm_min) + ":" + str(t.tm_sec) + ".0"
    json_data[sensor_name] = sensor_value
    print(json_data)
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

# Read and report sensor data, the return to sleep
from adafruit_seesaw.seesaw import Seesaw
import bitbangio
ss = Seesaw(bitbangio.I2C(board.A1, board.A0), addr=0x36)

pixel.fill((0, LUMINANCE, 0))

# read moisture level through capacitive touch pad
touch = ss.moisture_read()+ int(secrets["moisture"])
upload("moisture", str(touch))

# read temperature from the temperature sensor
temp = ss.get_temp() + int(secrets["temp"])
upload("temp", str(temp))

# go into low-power state for some number of seconds
pixel.fill((0, 0, 0))

import alarm
import time
# Create a an alarm that will trigger after a specified timer elapses.
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*5)
# Exit the program, and then deep sleep until the alarm wakes us.
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
# Does not return, so we never get here.