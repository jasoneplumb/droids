# file: main.py
# description: Show a random set of images and basenames every day
import badger2040
import machine
import os
import random
import time
display = badger2040.Badger2040()
# normal update speed is used to fully clear and show a fully saturated part of the phrase
display.update_speed(badger2040.UPDATE_NORMAL)
display.pen(15)
display.clear()
display.pen(0)
TEXT_SIZE = 25
def show( a, b, c ): # image paths for the three sections
    PATH_CHARS = 0#7 # 'images/'
    EXT_CHARS = 5 # '.jpeg'
    def chars(str):
        return len(str) - PATH_CHARS - EXT_CHARS    
    PIXELS = int(20 * TEXT_SIZE/40)
    display.text(a[PATH_CHARS:-EXT_CHARS], 0, badger2040.HEIGHT - PIXELS, TEXT_SIZE/40)
    display.text(b[PATH_CHARS:-EXT_CHARS], chars(a) * PIXELS, badger2040.HEIGHT - PIXELS, TEXT_SIZE/40)
    display.text(c[PATH_CHARS:-EXT_CHARS], (chars(a) + chars(b)) * PIXELS, badger2040.HEIGHT - PIXELS, TEXT_SIZE/40)
    return

A_IMAGES = os.listdir('images/a')
A_INDEX = random.randint(0,len(A_IMAGES)-1)
A_PATH = A_IMAGES[A_INDEX]

B_IMAGES = os.listdir('images/b')
B_INDEX = random.randint(0,len(B_IMAGES)-1)
B_PATH = B_IMAGES[B_INDEX]

C_IMAGES = os.listdir('images/c')
C_INDEX = random.randint(0,len(C_IMAGES)-1)
C_PATH = C_IMAGES[C_INDEX]

show(A_PATH, B_PATH, C_PATH)
display.update()
SECONDS_PER_DAY = 3
time.sleep(SECONDS_PER_DAY)
machine.reset()

