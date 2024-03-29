def Reading():
    result = None
    from adafruit_bme280 import basic as adafruit_bme280
    failure_count = 0
    success = False
    while not success:
        try:
            import board
            i2c = board.I2C()  # uses board.SCL and board.SDA
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            result = bme280.humidity
            success = True
        except Exception as error:
            failure_count += 1
            if failure_count >= 3:
                print("Failed to read bme280 (" + str(error) + ")")
                break
            print(".")
            import time
            time.sleep(5)
            continue
    if not success:
        from adafruit_am2320 import AM2320
        import bitbangio
        import board
        i2c = bitbangio.I2C(board.D12, board.D11)
        failure_count = 0
        success = False
        while not success:
            try:
                sensor = AM2320(i2c)
                result = sensor.relative_humidity
                success = True
            except Exception as error:
                failure_count += 1
                if failure_count >= 3:
                    print("Failed to read am2320 (" + str(error) + ")")
                    break
                print(".")
                import time
                time.sleep(5)
                continue
        i2c.deinit()
    return result

def Units():
    return 'percentage'
