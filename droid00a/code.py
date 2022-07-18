try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print(secrets["name"] + " droid" + secrets["droid_id"])

# Connect to AP
import board
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

def upload(sensor_name, sensor_value):
    attempts = 3  # Number of attempts to retry each request
    failure_count = 0
    response = None
    
    # Determine ts
    #import datetime
    #dt = datetime.datetime.now(datetime.timezone.utc)  
    #utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    #utc_timestamp = utc_time.timestamp()
    #print(utc_timestamp)

    # Upload a new sample
    json_data = \
    {
      "time_ts": "2022-07-17 18:00:21.000000",
      "droid_fk": droid_fk
    }
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
i2c_bus = board.I2C()
from adafruit_seesaw.seesaw import Seesaw
ss = Seesaw(i2c_bus, addr=0x36)
import time
while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()
    upload("moisture", str(touch))

    # read temperature from the temperature sensor
    temp = ss.get_temp()
    upload("temp", str(temp))

    # wait some number of seconds
    time.sleep(60*5)
