import pygame
import time
import os
import sys
from time import sleep
from pygame.locals import *

positionx = 10
positiony = 10
entireword = []
entireword_pos = 10
counter = 0
entire_newline = False


#Sets the width and height of the screen
WIDTH = 320
HEIGHT = 240
speed = 0.05

#Importing the external screen
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

#Initializes the screen - Careful: all pygame commands must come after the init
pygame.init()

#Sets mouse cursor visibility
pygame.mouse.set_visible(False)
#Sets the screen note: must be after pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.SysFont("monospace", 18)

#Class

class cursors(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.rect.center = (positionx + 10, positiony + 10)

    def update(self):
        self.rect.x = positionx + 10
        self.rect.y = positiony

#Functions

#Prints to the screen
def print_screen(words, speed):
    rel_speed = speed
    for char in words:
        #speed of writing
        if char == ".":
            sleep(0.3)
        else:
            sleep(rel_speed)

        #re-renders previous written letters
        global entireword

        # Old Typewriter functionality - Changes position of cursor and text a newline

        #Makes sure the previous letters are rendered and not lost
        #xx is a delimter so the program can see when to make a newline and ofcourse ignore writing the delimiter
        entireword.append(char)
        if counter > 0:
            loopcount = 1
            linecount = 0 # This is to which line we are on
            for prev in entireword:
                if prev == 'xx':
                    global linecount
                    global positiony
                    global loopcount
                    linecount = linecount + 1
                    positiony = 17 * linecount
                    loopcount = 1
                if prev != 'xx':  #ignore writing the delimiter
                    pchar = myfont.render(prev, 1, (255,255,0))
                    screen.blit(pchar, (loopcount * 10, positiony))
                    loopcount = loopcount + 1

        if char != 'xx':
            # render text
            letter = myfont.render(char, 1, (255,255,0))
            #blits the latest letter to the screen
            screen.blit(letter, (positionx, positiony))

        # Appends xx as a delimiter to indicate a new line
        if entire_newline == True:
            entireword.append('xx')
            global entire_newline
            entire_newline = False

        global positionx
        positionx = positionx + 10
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        screen.fill((0,0,0)) # blackens / clears the screen

        global counter
        counter = counter + 1

#Positions cursor at new line
def newline():
    global positionx
    global positiony
    positionx = 10
    positiony = positiony + 17

all_sprites = pygame.sprite.Group()
cursor = cursors()
all_sprites.add(cursor)

#Main loop
running = True
while running:
    global speed
    global entire_newline

    words = "[i] Initializing ..."
    entire_newline = True
    newline()
    print_screen(words,speed)

    words = "[i] Entering ghost mode ..."
    entire_newline = True
    newline()
    print_screen(words,speed)

    #Stops the endless loop if False
    running = False
sleep(10)