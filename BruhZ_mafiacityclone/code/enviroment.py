"""
everything related to world, like walls, lamps etc
"""

import pygame
from Autoload import *


class Block(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__([all_sprites, collide_sprites])
        self.image = pygame.Surface((64,64))
        self.rect = self.image.get_rect(topleft = pos)

        self.collideable = True










