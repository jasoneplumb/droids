# file: main.py
# description: Show a random set of images and base names every day
#from micropython import const
import time
import machine
import badger2040
import os
import random
import sys

SIZE = 0.35
TEXT_Y = badger2040.HEIGHT - 5
PIXELS_PER_IMAGE = 37888 # equals 296 * 128
BYTES_PER_IMAGE = PIXELS_PER_IMAGE // 8
PEN_WHITE = 15
BLACK = 0

def ShowMessage( msg ):
    display.pen(BLACK)
    display.text(msg, 0, TEXT_Y, SIZE)
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
    A_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("images/a/{}".format(a), "rb").readinto(A_IMAGE)
    B_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("images/b/{}".format(b), "rb").readinto(B_IMAGE)
    C_IMAGE = bytearray(BYTES_PER_IMAGE)
    open("images/c/{}".format(c), "rb").readinto(C_IMAGE)
    COMPOSITE_IMAGE = bytearray(BYTES_PER_IMAGE)
    index = BYTES_PER_IMAGE - 1
    while index >= 0:
        COMPOSITE_IMAGE[index] = A_IMAGE[index] + B_IMAGE[index] + C_IMAGE[index]
        index = index - 1
    display.image(COMPOSITE_IMAGE)
    return

# Show a random set of images and base names every day
# The A image is on the top
badger2040.system_speed(badger2040.SYSTEM_VERY_SLOW) # 4 Mhz
display = badger2040.Badger2040()
while (1):
    A_IMAGES = BinFilesIn('images/a')
    if (len(A_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin found in /images/a/')
    A_INDEX = random.randint(0,len(A_IMAGES)-1)
    A_PATH = A_IMAGES[A_INDEX]
    # The B image is in the middle
    B_IMAGES = BinFilesIn('images/b')
    if (len(B_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin found in /images/b/')
    B_INDEX = random.randint(0,len(B_IMAGES)-1)
    B_PATH = B_IMAGES[B_INDEX]
    # The C image appears below the other two
    C_IMAGES = BinFilesIn('images/c')
    if (len(C_IMAGES) == 0): ShowErrorMessageAndExit('ERROR: No .bin found in /images/c/')
    C_INDEX = random.randint(0,len(C_IMAGES)-1)
    C_PATH = C_IMAGES[C_INDEX]
    NAME = A_PATH[:-4] + B_PATH[:-4] + C_PATH[:-4]
    print( NAME )
    ShowImages(A_PATH, B_PATH, C_PATH)
    display.update()
    if (0):
        display.halt() # press any key to advance to next pick
    else:
        time.sleep(43200) # 43200 = 12 hours * 60 minutes * 60 seconds
    
