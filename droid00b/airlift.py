def Esp():
    MINUTES_BETWEEN_RETRIES = 1
    import board
    import neopixel
    np = neopixel.NeoPixel(board.NEOPIXEL, 1)
    np.brightness = 1.0
    BLUE = (0, 0, 5)
    np.fill(BLUE)
    from digitalio import DigitalInOut
    esp32_cs = DigitalInOut(board.D10)
    esp32_ready = DigitalInOut(board.D9)
    esp32_reset = DigitalInOut(board.D6)
    from adafruit_esp32spi import adafruit_esp32spi
    import busio
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    while not esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        continue
    try:
        import json
        config_file = open('configuration.json')
        config = json.load(config_file)
        config_file.close()
        esp.connect_AP(config['ssid'], config['password'])
    except Exception as error:
        print(str(error))
    np.deinit()
    if esp.is_connected:
        return esp
    else:
        return None