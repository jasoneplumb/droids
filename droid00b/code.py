# droid00b: periodic upload of local greenhouse sensor data
# TODO test new barometer
# TODO factor out, as a function, the multi-pass try/catch pattern
# TODO factor out, as a file, each sensor's logic
# TODO Add support for sensor specific sampling frequencies
MINUTES_BETWEEN_SAMPLES = 1

# Indicate that we are starting up   
import board
import neopixel
import time
neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
neopixel.brightness = 1.0
for v in range(0, 5, 1):
    neopixel.fill((v, v, v))
    time.sleep(0.1)

# Enter a low power state for the specified number of minutes,
# before restarting the device (program).
def deep_sleep_then_restart(minutes):
    print("Entering deep sleep for", minutes, "minutes before restarting")
    for v in range(5, 0, -1):
        neopixel.fill((v, v, v))
        time.sleep(0.1)
    neopixel.deinit()
    import alarm
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*minutes)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm) # DOES NOT RETURN

# Ensure that the secrets file is valid
try:
    from secrets import secrets
    print(secrets['droid_name'] + " (droid" + secrets['droid_id'] + ")")
except ImportError:
    print("Error: secrets.py not found!")
    RED = (5, 0, 0)
    neopixel.fill(RED) 
    raise

# Read sensors
import bitbangio
i2csoil = bitbangio.I2C(board.A1, board.A0)
i2csoil.try_lock()
soil_sensor_found = True
i2cdevices = i2csoil.scan()
print(i2cdevices)
if (len(i2cdevices) == 0):
    soil_sensor_found = False
    print("Warning: soil_moisture and soil_temperature sensors not found!")
i2csoil.unlock()
if soil_sensor_found:
    from adafruit_seesaw.seesaw import Seesaw 
    ss = Seesaw(i2csoil, addr=0x36)
    # Read sensor values and add sensor bias
    soil_moisture = ss.moisture_read() + secrets['soil_moisture']
    time.sleep(0.2) # sensors cannot be read back to back, need small delay
    soil_temperature = ss.get_temp() + secrets['soil_temperature']
    print("soil_moisture: " + str(soil_moisture))
    print("soil_temperature: " + str(soil_temperature))

from analogio import AnalogIn
def get_voltage(pin):
    return (pin.value * 3.3) / 65536
uv_index = (get_voltage(AnalogIn(board.A3)) * 10) + secrets['uv_index']
print("uv_index: " + str(uv_index))

relative_humidity = None
temperature = None
from adafruit_bme280 import basic as adafruit_bme280
failure_count = 0
success = False
while not success:
    try:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        relative_humidity = bme280.humidity + secrets['relative_humidity']
        temperature = bme280.temperature + secrets['temperature']
        success = True
    except Exception as error:
        failure_count += 1
        if failure_count >= 3:
            print("Failed to read am2320 (" + str(error) + ")")
            break
        time.sleep(5)
        continue
if (relative_humidity != None): print("relative_humidity: " + str(relative_humidity))
if (temperature != None): print("temperature: " + str(temperature))

# Attach to the network
BLUE = (0, 0, 5)
neopixel.fill(BLUE)
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
        esp.connect_AP(secrets['ssid'], secrets['password'])
    except Exception as error:
        failure_count += 1
        if failure_count >= 3:
            print("Error: Failed to get connect (" + str(error) + ")")
            deep_sleep_then_restart(MINUTES_BETWEEN_SAMPLES)
        time.sleep(5)
        print("Warning: Retrying AP connection!")
        continue
print("ESP firmware: ", esp.firmware_version)
print("Connected to ", str(esp.ssid, "utf-8"), ", ", esp.pretty_ip(esp.ip_address), "(RSSI is ", esp.rssi, ")")
if esp.rssi < -70:
    print("warning: Below minimum signal strength for reliable packet delivery")
    YELLOW = (5, 5, 0)
    neopixel.fill(YELLOW)
else:
    GREEN = (0, 5, 0)
    neopixel.fill(GREEN)

# Compose the JSON data object to upload
UTC = None
UTC_response = None
failure_count = 0
while not UTC_response:
    try:
        UTC_response = requests.get('http://worldclockapi.com/api/json/utc/now')
    except Exception as error:
        print(".")
        failure_count += 1
        if failure_count >= 3:
            print("Failed to get UTC (" + str(error) + ")")
            deep_sleep_then_restart(MINUTES_BETWEEN_SAMPLES)
        print("Warning: Retrying UTC request!")
        time.sleep(5)
        continue
UTC = UTC_response.json()['currentDateTime'][:-1] # Removes the trailing 'Z'
UTC_response.close()
UTC_response = None
print('UTC is ' + UTC)

def upload(sensor_group_name, sensor_name, sensor_value, ts):
    # upload a new sample
    json_data = \
    {
        "droid_fk": secrets['droid_fk'],
        "time_ts": UTC
    }
    json_data[sensor_name] = sensor_value
    TABLES = "https://vcgtjqigra.execute-api.us-west-2.amazonaws.com/proto/sensor_droid"
    TABLE = TABLES + "/" + sensor_group_name
    print(f"PUTing data to {TABLE} {json_data}")
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
                deep_sleep_then_restart(MINUTES_BETWEEN_SAMPLES)
            print("Warning: Retrying data upload!")
            time.sleep(5)
            continue
    print(response.text)
    response.close()
    response = None
    
# upload sensor data
upload("rssi", "rssi", str(esp.rssi), UTC)
upload("uv", "uv_index", str(uv_index), UTC)
if (relative_humidity != None): upload("relative_humidity", "relative_humidity", str(relative_humidity), UTC)
if (temperature != None): upload("temperature", "temperature", str(temperature), UTC)
if (soil_sensor_found):
    upload("soil_temperature", "temp_temperature", str(soil_temperature), UTC)
    upload("soil_moisture", "soil_moisture", str(soil_moisture), UTC)

# shutdown
esp.disconnect()
print("Disconnected from", secrets['ssid'])
deep_sleep_then_restart(MINUTES_BETWEEN_SAMPLES)
