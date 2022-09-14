# droid00b: periodic upload of local greenhouse sensor data
# TODO factor out, as a function, the multi-pass try/catch pattern
# TODO Add support for sensor specific sampling frequencies

# droid00b = {
#     'description': {
#         'sensors': [{
#             'pretty_name': 'Relative Humidity', 
#             'endpoint': 'proto/sensor_droid/relative_humidity', 
#             'reading_column_name': 'relative_humidity',
#             'reading_units': 'Percentage', 
#             'period': '3', 
#             'period_units': 'hours',
#             'precision': '0.1', 
#             'accuracy': '0.01'
#         }, {
#             'pretty_name': 'Wi-Fi Signal Strength', 
#             'endpoint': 'proto/sensor_droid/rssi', 
#             'reading_column_name': 'rssi',
#             'reading_units': 'RSSI', 
#             'period': '1', 
#             'period_units': 'days',
#             'precision': '1.0', 
#             'accuracy': '0.1'
#         }, {
#             'pretty_name': 'Soil Moisture', 
#             'endpoint': 'proto/sensor_droid/soil_moisture', 
#             'reading_column_name': 'soil_moisture',
#             'reading_units': 'Percentage', 
#             'period': '3', 
#             'period_units': 'hours',
#             'precision': '1.0', 
#             'accuracy': '5.0'
#         }, {
#             'pretty_name': 'Soil Temperature', 
#             'endpoint': 'proto/sensor_droid/soil_temperature', 
#             'reading_column_name': 'soil_temperature',
#             'reading_units': 'Celcius', 
#             'period': '1', 
#             'period_units': 'hours',
#             'precision': '0.01', 
#             'accuracy': '2.0'
#         }, {
#             'pretty_name': 'Ambient Temperature', 
#             'endpoint': 'proto/sensor_droid/temperature', 
#             'reading_column_name': 'temperature',
#             'reading_units': 'Celcius', 
#             'period': '30', 
#             'period_units': 'minutes',
#             'precision': '0.1', 
#             'accuracy': '0.01'
#         }, {
#             'pretty_name': 'Ultraviolet Radiation', 
#             'endpoint': 'proto/sensor_droid/uv', 
#             'reading_column_name': 'uv_index',
#             'reading_units': 'UV Index', 
#             'period': '3', 
#             'period_units': 'hours',
#             'precision': '0.1', 
#             'accuracy': '0.01'
#         }]
#     }
# }

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
import soil_moisture
sm = soil_moisture.Reading()
if (sm != None): print('soil_moisture is '+ str(sm) + ' (' + soil_moisture.Units() + ')')
import soil_temperature
st = soil_temperature.Reading()
if (st != None): print('soil_temperature is '+ str(st) + ' (' + soil_temperature.Units() + ')')
import uv_index
uv = uv_index.Reading()
if (uv != None): print('uv_index is '+ str(uv) + ' (' + uv_index.Units() + ')')
import relative_humidity
rh = relative_humidity.Reading()
if (rh != None): print('relative_humidity is '+ str(rh) + ' (' + relative_humidity.Units() + ')')
import temperature
t = temperature.Reading()
if (t != None): print('temperature is '+ str(t) + ' (' + temperature.Units() + ')')

# Attach to the network
MINUTES_BETWEEN_RETRIES = 1
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
            deep_sleep_then_restart(MINUTES_BETWEEN_RETRIES)
        print(".")
        time.sleep(5)
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
            deep_sleep_then_restart(MINUTES_BETWEEN_RETRIES)
        print("Warning: Retrying UTC request!")
        time.sleep(5)
        continue
UTC = UTC_response.json()['currentDateTime'][:-1] # Removes the trailing 'Z'
UTC_response.close()
UTC_response = None
print('UTC is ' + UTC)

def upload(sensor_group_name, sensor_name, sensor_value, ts):
    if (sensor_value == None):
        return
    # upload a new sample
    json_data = \
    {
        "droid_fk": secrets['droid_fk'],
        "time_ts": UTC
    }
    json_data[sensor_name] = str(sensor_value)
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
                deep_sleep_then_restart(MINUTES_BETWEEN_RETRIES)
            print("Warning: Retrying data upload!")
            time.sleep(5)
            continue
    print(response.text)
    response.close()
    response = None
    
# upload sensor data
upload("rssi", "rssi", esp.rssi, UTC)
upload("soil_moisture", "soil_moisture", sm, UTC)
upload("soil_temperature", "soil_temperature", st, UTC)
upload("uv", "uv_index", uv, UTC)
upload("relative_humidity", "relative_humidity", rh, UTC)
upload("temperature", "temperature", t, UTC)

# shutdown
esp.disconnect()
print("Disconnected from", secrets['ssid'])
deep_sleep_then_restart(MINUTES_BETWEEN_RETRIES)
