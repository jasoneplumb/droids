# droid00b: periodic upload of local greenhouse sensor data
# TODO factor out, as a function, the multi-pass try/catch pattern
# TODO Add support for sensor specific sampling frequencies

import rp2040
rp2040.startup()
import board
import neopixel
np = neopixel.NeoPixel(board.NEOPIXEL, 1)
np.brightness = 1.0
WHITE = (5, 5, 5)
np.fill(WHITE)
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
np.deinit()

# Connect to the network
MINUTES_BETWEEN_RETRIES = 1
import airlift
esp = airlift.Esp()
if (esp != None):
    import adafruit_esp32spi.adafruit_esp32spi_socket as socket
    import adafruit_requests as requests
    requests.set_socket(socket, esp)
    import json
    config_file = open('configuration.json')
    config = json.load(config_file)
    config_file.close()
    def upload(sensor_group_name, sensor_name, sensor_value, ts):
        if (sensor_value == None):
            return
        # upload a new sample
        json_data = {
            "droid_fk": config['droid_fk'],
            "sample_time": ts
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
                    rp2040.restart(MINUTES_BETWEEN_RETRIES)
                print("Warning: Retrying data upload!")
                import time
                time.sleep(5)
                continue
        print(response.text)
        response.close()
        response = None
        failure_count = 0
    
    np = neopixel.NeoPixel(board.NEOPIXEL, 1)
    np.brightness = 1.0
    YELLOW = (5, 5, 0)
    np.fill(YELLOW)
    failure_count = 0
    UTC_response = None
    while not UTC_response:
        try:
            UTC_response = requests.get('http://worldclockapi.com/api/json/utc/now')
        except Exception as error:
            print(".")
            failure_count += 1
            if failure_count >= 3:
                print("Failed to get UTC (" + str(error) + ")")
                rp2040.restart(MINUTES_BETWEEN_RETRIES)
            print("Warning: Retrying UTC request!")
            import time
            time.sleep(5)
            continue
    UTC = UTC_response.json()['currentDateTime'][:-1] # Removes the trailing 'Z'
    UTC_response.close()
    UTC_response = None
    np.deinit()

    np = neopixel.NeoPixel(board.NEOPIXEL, 1)
    np.brightness = 1.0
    GREEN = (0, 5, 0)
    np.fill(GREEN)
    upload("rssi", "rssi", esp.rssi, UTC)
    upload("soil_moisture", "soil_moisture", sm, UTC)
    upload("soil_temperature", "soil_temperature", st, UTC)
    upload("uv", "uv_index", uv, UTC)
    upload("relative_humidity", "relative_humidity", rh, UTC)
    upload("temperature", "temperature", t, UTC)
    esp.disconnect()
    np.deinit()
rp2040.restart(MINUTES_BETWEEN_RETRIES)
