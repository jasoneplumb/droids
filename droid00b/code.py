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
    def upload(sensor_group_name, sensor_name, sensor_value, ts):
        if (sensor_value == None):
            return
        # upload a new sample
        from secrets import secrets    
        json_data = \
        {
            "droid_fk": secrets['droid_fk'],
            "time_ts": ts
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