import sys
import time
import pygame
from loops import  Loops
from settings import *



pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE), flags = FLAGS)
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
loops = Loops()

next_time = time.time()
dt = 0



while True:
    dt = time.time() - next_time
    next_time = time.time()

    loops.input_handler()
    loops.update_handler(dt)
    loops.display_handler()

    pygame.display.flip()
    clock.tick(FPS)






