import board
import neopixel
import time

def startup():
    np = neopixel.NeoPixel(board.NEOPIXEL, 1)
    np.brightness = 1.0
    for v in range(0, 5, 1):
        np.fill((v, v, v))
        time.sleep(0.1)
    np.deinit()

def restart(minutes):
    np = neopixel.NeoPixel(board.NEOPIXEL, 1)
    np.brightness = 1.0
    print("Entering deep sleep for", minutes, "minutes before restarting")
    for v in range(5, 0, -1):
        np.fill((v, v, v))
        time.sleep(0.1)
    np.deinit()
    import alarm
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60*minutes)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm) 
    # DOES NOT RETURN

