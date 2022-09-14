def Reading():
    import bitbangio
    import board
    i2csoil = bitbangio.I2C(board.A1, board.A0)
    i2csoil.try_lock()
    i2cdevices = i2csoil.scan()
    i2csoil.unlock()
    if (len(i2cdevices)>0):
        from adafruit_seesaw.seesaw import Seesaw 
        ss = Seesaw(i2csoil, addr=0x36)
        result = ss.moisture_read()
        result /= 20 # convert to RH%
    i2csoil.deinit()
    return result

def Units():
    return 'Percentage'