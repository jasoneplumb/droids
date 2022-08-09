# droid00b: periodic upload of local greenhouse sensor data

import neopixel
import board
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 1.0
WHITE = (5, 5, 5)
BLACK = (0, 0, 0)
RED = (5, 0, 0)
YELLOW = (5, 5, 0)
GREEN = (0, 5, 0)
CYAN = (0, 5, 5)
BLUE = (0, 0, 5)

import time
def pixel_flash(color):
    pixel.fill(color)
    time.sleep(0.1)
for v in range(0, 5, 1):
    pixel_flash((v, v, v))
    
if False:
    import time
    import board

    i2c = board.I2C()
    # i2c = busio.I2C(board.SCL1, board.SDA1)  # QT Py RP2040 STEMMA connector
    # i2c = busio.I2C(board.GP1, board.GP0)    # Pi Pico RP2040

    while not i2c.try_lock():
        pass
    try:
        while True:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in i2c.scan()],
            )
            time.sleep(2)
    finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
        i2c.unlock()

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print(secrets["name"] + " (droid" + secrets["droid_id"] + ")")

# Read detected sensor data
import bitbangio
i2c = bitbangio.I2C(board.A1, board.A0)
i2c.try_lock()
soil_sensor_found = True
i2cdevices = i2c.scan()
#print(i2cdevices)
if (len(i2cdevices) > 20):
    soil_sensor_found = False
    print("Warning: soil sensors not found!")
i2c.unlock()
if soil_sensor_found:
    from adafruit_seesaw.seesaw import Seesaw 
    ss = Seesaw(i2c, addr=0x36) # soil moisture and temp
    # Read sensor values and add sensor bias
    moisture = ss.moisture_read() + secrets["soil_moisture"]
    temp = ss.get_temp() + secrets["soil_temp"]
from analogio import AnalogIn
def get_voltage(pin):
    return (pin.value * 3.3) / 65536
uv_index = get_voltage(AnalogIn(board.A3)) * 10

# Conneting to Access Point
pixel.fill(BLUE)
from digitalio import DigitalInOut
esp32_cs = DigitalInOut(board.D10)
esp32_ready = DigitalInOut(board.D9)
esp32_reset = DigitalInOut(board.D6)
from adafruit_esp32spi import adafruit_esp32spi
import busio
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
requests.set_socket(socket, esp)
while not esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    continue
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except OSError as e:
        print(".")
        continue
print("Connected to ", str(esp.ssid, "utf-8"), ", ", esp.pretty_ip(esp.ip_address), "(RSSI is ", esp.rssi, ")")

# Warn about low signal strength
if esp.rssi < -70:
    print("warning: Below minimum signal strength for reliable packet delivery")
    pixel.fill(YELLOW)
else:
    pixel.fill(GREEN)

def upload(sensor_group_name, sensor_name, sensor_value):
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
    TABLE = TABLES + "/" + sensor_group_name
    print("PUTing data to {0}: {1}".format(TABLE, json_data))
    while not response:
        try:
            response = requests.put(TABLE, json=json_data)
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
    
# Uploading data
upload("uv", "uv_index", str(uv_index))
if (soil_sensor_found):
    upload("soil_moisture", "moisture", str(moisture))
    upload("soil_temp", "temp", str(temp))

# Signal successful shutdown
for v in range(5, 0, -1):
    pixel_flash((v, v, v))
pixel.deinit()
    
# Create a an alarm that will trigger after a specified timer elapses.
import alarm
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*5)
# Exit the program, and then deep sleep until the alarm wakes us.
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
# Does not return. When the timer elapses, the program restarts.

