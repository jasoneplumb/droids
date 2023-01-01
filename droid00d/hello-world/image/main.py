# file: main.py
# description: Render simple text using different saturation levels
import badger2040
import machine
import time
display = badger2040.Badger2040()
# normal update speed is used to fully clear and show a fully saturated part of the phrase
display.update_speed(badger2040.UPDATE_NORMAL)
display.pen(15)
display.clear()
display.pen(0)
HALF_H = int(badger2040.HEIGHT/2)
display.text("Hello", 0, HALF_H, rotation=0)
display.update()
# turbo update speed is used to refill the phrase quickly...each press shows the next level (16?) of saturation
display.update_speed(badger2040.UPDATE_TURBO)
running = True
while running:
    # handle button functionality
    if display.pressed(badger2040.BUTTON_A):
        running = False
    if display.pressed(badger2040.BUTTON_B):
        # render the full phrase      
        display.text("Hello World", 0, HALF_H, rotation=0)
        display.update()
    # limit the sampling rate to ten per second
    time.sleep(.1)

machine.reset()
# <end of program>

