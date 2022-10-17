def Reading():
    import bitbangio
    import board
    i2csoil = bitbangio.I2C(board.A1, board.A0)
    i2csoil.try_lock()
    i2cdevices = i2csoil.scan()
    i2csoil.unlock()
    result = None
    if (len(i2cdevices)>0):
        failure_count = 0
        success = False
        while not success:
            try:
                from adafruit_seesaw.seesaw import Seesaw 
                ss = Seesaw(i2csoil, addr=0x36)
                result = ss.moisture_read()
                result /= 20 # convert to RH%
                success = True
            except Exception as error:
                failure_count += 1
                if failure_count >= 3:
                    print("Failed to read soil_moisture (" + str(error) + ")")
                    break
                print(".")
                import time
                time.sleep(5)
                continue
    i2csoil.deinit()
    return result

def Units():
    return 'percentage'
