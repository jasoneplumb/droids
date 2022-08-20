# droid00b: periodic upload of local greenhouse sensor data

import neopixel
import board
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 1.0
RED = (5, 0, 0)
YELLOW = (5, 5, 0)
GREEN = (0, 5, 0)
BLUE = (0, 0, 5)

def deep_sleep(minutes):
    print("Entering deep sleep for", minutes, "minutes before restarting")
    for v in range(5, 0, -1):
        pixel_flash((v, v, v))
    pixel.deinit()
    import alarm
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*minutes)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm) # DOES NOT RETURN

import time
def pixel_flash(color):
    pixel.fill(color)
    time.sleep(0.1)
for v in range(0, 5, 1):
    pixel_flash((v, v, v))
  
try:
    from secrets import secrets
    print(secrets["name"] + " (droid" + secrets["droid_id"] + ")")
except ImportError:
    print("Error: secrets.py not found!")
    pixel.fill(RED) 
    raise

# read sensor data
import bitbangio
i2csoil = bitbangio.I2C(board.A1, board.A0)
i2csoil.try_lock()
soil_sensor_found = True
i2cdevices = i2csoil.scan()
if (len(i2cdevices) == 0):
    soil_sensor_found = False
    print("Warning: soil_moisture and soil_temperature sensors not found!")
i2csoil.unlock()
if soil_sensor_found:
    from adafruit_seesaw.seesaw import Seesaw 
    ss = Seesaw(i2csoil, addr=0x36)
    # Read sensor values and add sensor bias
    soil_moisture = ss.moisture_read() + secrets["soil_moisture"]
    time.sleep(0.2) # sensors cannot be read back to back, need small delay
    soil_temperature = ss.get_temp() + secrets["soil_temperature"]
    print("soil_moisture: " + str(soil_moisture))
    print("soil_temperature: " + str(soil_temperature))

from analogio import AnalogIn
def get_voltage(pin):
    return (pin.value * 3.3) / 65536
uv_index = (get_voltage(AnalogIn(board.A3)) * 10) + secrets["uv_index"]
print("uv_index: " + str(uv_index))

# import adafruit_am2320
# failure_count = 0
# success = False
# while not success:
#     try:
#         i2cam = bitbangio.I2C(board.D12, board.D11)
#         am = adafruit_am2320.AM2320(i2cam)
#         relative_humidity = am.relative_humidity + secrets["relative_humidity"]
#         temperature = am.temperature + secrets["temperature"]
#         success = True
#     except Exception as error:
#         failure_count += 1
#         if failure_count >= 3:
#             print("Failed to read am2320 (" + str(error) + ")")
#             deep_sleep(5)
#         print(".")
#         time.sleep(3)
#         continue
# print("relative_humidity: " + str(relative_humidity))
# print("temperature: " + str(temperature))
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
failure_count = 0
while not esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    continue
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except Exception as error:
        failure_count += 1
        if failure_count >= 3:
            print("Error: Failed to get connect (" + str(error) + ")")
            deep_sleep(1)
        time.sleep(5)
        print("Warning: Retrying AP connection!")
        continue
print("ESP firmware: ", esp.firmware_version)
print("Connected to ", str(esp.ssid, "utf-8"), ", ", esp.pretty_ip(esp.ip_address), "(RSSI is ", esp.rssi, ")")

# warn about low signal strength
if esp.rssi < -70:
    print("warning: Below minimum signal strength for reliable packet delivery")
    pixel.fill(YELLOW)
else:
    pixel.fill(GREEN)

# get the time stamp (ts)
ts = None
ts_res = None
failure_count = 0
while not ts_res:
    try:
        ts_res = requests.get('http://worldclockapi.com/api/json/utc/now')
    except Exception as error:
        print(".")
        failure_count += 1
        if failure_count >= 3:
            print("Failed to get UTC (" + str(error) + ")")
            deep_sleep(1)
        print("Warning: Retrying UTC request!")
        time.sleep(5)
        continue
ts = ts_res.json()['currentDateTime'][:-1]
ts_res.close()
ts_res = None

print('UTC is ' + ts)

def upload(sensor_group_name, sensor_name, sensor_value, ts):
    # upload a new sample
    json_data = \
    {
        "droid_fk": secrets['droid_fk'],
        "time_ts": ts
    }
    json_data[sensor_name] = sensor_value
    TABLES = "https://vcgtjqigra.execute-api.us-west-2.amazonaws.com/proto/sensor_droid"
    TABLE = TABLES + "/" + sensor_group_name
    print("PUTing data to {0}: {1}".format(TABLE, json_data))
    failure_count = 0
    response = None
    while not response:
        try:
            response = requests.put(TABLE, json=json_data)
        except Exception as error:
            print(".")
            failure_count += 1
            if failure_count >= 3:
                print("Failed to upload sensor data (" + str(error) + ")")
                deep_sleep(1)
            print("Warning: Retrying data upload!")
            time.sleep(5)
            continue
    print(response.text)
    response.close()
    response = None
    
# upload sensor data
if (soil_sensor_found):
    upload("soil_moisture", "soil_moisture", str(soil_moisture), ts)
    upload("soil_temp", "temp", str(soil_temperature), ts)
upload("uv", "uv_index", str(uv_index), ts)
#upload("relative_humidity", "relative_humidity", str(relative_humidity), ts)
#upload("temperature", "temperature", str(temperature), ts)
upload("rssi", "rssi", str(esp.rssi), ts)

# shutdown
esp.disconnect()
print("Disconnected from", secrets['ssid'])
deep_sleep(1)
# EOF
