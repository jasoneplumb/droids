# file: main.py
# description: Shows a random combination of top, middle, and bottom images twice a day.

from micropython import const
from machine import Pin, ADC
import badger2040
import os
import random
import sys
import time

MIN_BATTERY_VOLTAGE = 2.4
MAX_BATTERY_VOLTAGE = 3.7	
# Starting point for LiPo battery is 3.2 - 4.0
#MIN_BATTERY_VOLTAGE = 3.2
#MAX_BATTERY_VOLTAGE = 4.0
# Starting point for 2xAAA batteries is 3.0 - 3.4
#MIN_BATTERY_VOLTAGE = 3.0
#MAX_BATTERY_VOLTAGE = 3.4

WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT
BATT_HEIGHT = const(8) # Max thickness of 8 matches partial update accomodation (below)
BATT_WIDTH = const(32)
TEXT_Y = HEIGHT - 5
TEXT_X = BATT_WIDTH + 5
PIXELS_PER_IMAGE = const(37888) # equals 296 * 128
BYTES_PER_IMAGE = const(PIXELS_PER_IMAGE // 8)
BATT_BORDER = 1
BATT_TERM_WIDTH = 2
BATT_TERM_HEIGHT = BATT_HEIGHT - 2
H_OFFSET = -131 + BATT_TERM_WIDTH
V_OFFSET = 68 - BATT_HEIGHT
BATT_BAR_PADDING = 0
BATT_BAR_HEIGHT = BATT_HEIGHT - (BATT_BORDER * 2) - (BATT_BAR_PADDING * 2)
BATT_BAR_START = ((WIDTH - BATT_WIDTH) // 2) + BATT_BORDER + BATT_BAR_PADDING
BATT_BAR_END = ((WIDTH + BATT_WIDTH) // 2) - BATT_BORDER - BATT_BAR_PADDING
NUM_BATT_BARS = 10

def DrawBattery(level, max_level):
    # Draw the battery outline as two rects
    display.pen(0)
    display.rectangle(
        H_OFFSET + (WIDTH - BATT_WIDTH) // 2,
        V_OFFSET + (HEIGHT - BATT_HEIGHT) // 2,
        BATT_WIDTH,
        BATT_HEIGHT
    )
    display.pen(15) # smaller white inner portion
    display.rectangle(
        H_OFFSET + (WIDTH - BATT_WIDTH) // 2 + BATT_BORDER,
        V_OFFSET + (HEIGHT - BATT_HEIGHT) // 2 + BATT_BORDER,
        BATT_WIDTH - BATT_BORDER * 2,
        BATT_HEIGHT - BATT_BORDER * 2,
    )
    display.pen(0)

    # Draw the battery positive terminal (+)
    display.rectangle(
        H_OFFSET + (WIDTH + BATT_WIDTH) // 2 - BATT_WIDTH - BATT_TERM_WIDTH,
        V_OFFSET + (HEIGHT - BATT_TERM_HEIGHT) // 2,
        BATT_TERM_WIDTH,
        BATT_TERM_HEIGHT,
    )

    # Draw the battery bars
    length = (BATT_BAR_END - BATT_BAR_START - ((NUM_BATT_BARS - 1) * BATT_BAR_PADDING)) // NUM_BATT_BARS
    current_level = 0.0
    normalised_level = level / max_level
    for i in range(NUM_BATT_BARS):
        current_level = (1.0 * i) / NUM_BATT_BARS
        if normalised_level > current_level:
            pos = (NUM_BATT_BARS-1-i) * (length + BATT_BAR_PADDING)
            display.rectangle(
                H_OFFSET + BATT_BAR_START + pos,
                V_OFFSET + (HEIGHT - BATT_BAR_HEIGHT) // 2,
                length,
                BATT_BAR_HEIGHT,
            )

def ShowMessage( msg ):
    display.text(msg, TEXT_X, TEXT_Y, 0.4)
    return

def ShowErrorMessageAndExit( msg ):
    ShowMessage(msg)
    display.update()
    sys.exit(-1) # end continued execution of the program
    return

def BinFilesIn( path ): # returns an array of .bin files in the specified directory
    result = []
    try:
        result = [f for f in os.listdir(path) if f.endswith(".bin")]
    except (OSError, ImportError):
        pass
    return result

def ShowImages( a, b, c ): # image file names of the three portions
    # Compose and display the image data associated with the provided file names
    TOP_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("top/{}".format(a), "rb").readinto(TOP_IMAGE)
    MIDDLE_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("middle/{}".format(b), "rb").readinto(MIDDLE_IMAGE)
    BOTTOM_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("bottom/{}".format(c), "rb").readinto(BOTTOM_IMAGE)
    COMPOSITE_IMAGE = bytearray(BYTES_PER_IMAGE)
    index = BYTES_PER_IMAGE - 1
    while index >= 0:
        COMPOSITE_IMAGE[index] = TOP_IMAGE[index] + MIDDLE_IMAGE[index] + BOTTOM_IMAGE[index]
        index = index - 1
    display.image(COMPOSITE_IMAGE)
    return

# Set up the ADCs for measuring battery voltage
vbat_adc = ADC(badger2040.PIN_BATTERY)
vref_adc = ADC(badger2040.PIN_1V2_REF)
vref_en = Pin(badger2040.PIN_VREF_POWER)
vref_en.init(Pin.OUT)
vref_en.value(0)

def map_value(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min

badger2040.system_speed(badger2040.SYSTEM_VERY_SLOW) # 4 Mhz
display = badger2040.Badger2040()
while True:
    vref_en.value(1) # Enable the onboard voltage reference
    vdd = 1.24 * (65535 / vref_adc.read_u16()) # Calculate the logic supply voltage
    vbat = vdd * 3 * vbat_adc.read_u16() / 65535 # 3 is gain
    vref_en.value(0) # Disable the onboard voltage reference
    level = int(map_value(vbat, MIN_BATTERY_VOLTAGE, MAX_BATTERY_VOLTAGE, 0, NUM_BATT_BARS))
    DrawBattery(level, NUM_BATT_BARS)
    TOP_IMAGES = BinFilesIn('top')
    if (len(TOP_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin files found in top/')
    TOP_INDEX = random.randint(0,len(TOP_IMAGES)-1)
    TOP_PATH = TOP_IMAGES[TOP_INDEX]
    MIDDLE_IMAGES = BinFilesIn('middle')
    if (len(MIDDLE_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin files found in middle/')
    MIDDLE_INDEX = random.randint(0,len(MIDDLE_IMAGES)-1)
    MIDDLE_PATH = MIDDLE_IMAGES[MIDDLE_INDEX]
    BOTTOM_IMAGES = BinFilesIn('bottom')
    if (len(BOTTOM_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin files found in bottom/')
    BOTTOM_INDEX = random.randint(0,len(BOTTOM_IMAGES)-1)
    BOTTOM_PATH = BOTTOM_IMAGES[BOTTOM_INDEX]
#    NAME = TOP_PATH[:-4] + MIDDLE_PATH[:-4] + BOTTOM_PATH[:-4]
#    print("Measured battery at ", vbat, "v", sep="") # debugging only
#    ShowMessage(NAME) # Removed until names are updated and partial update is fixed
    if (vbat > MIN_BATTERY_VOLTAGE):
#        display.partial_update(0, 120, 296, 8)
        ShowImages(TOP_PATH, MIDDLE_PATH, BOTTOM_PATH)
#        display.partial_update(0, 0, 296, 120)
#    else:
    display.update()
    time.sleep(43200) # 43200 = 12 hours * 60 minutes * 60 seconds
