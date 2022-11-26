import pygame, sys
from entities import *
from enviroment import *
from objects import *
from Autoload import *




class Loops:
    def __init__(self):
        #test sprites
        self.player =Player((200,100))
        Block((500,500))
        Block((300, 500))
        Block((100, 500))

        ToPickRevolver((140,100))
        ToPickFastGun((140, 120))

        NPC_Basic((400,300))

    def input_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.player.input()

    def display_handler(self):
        pygame.display.get_surface().fill((100, 100, 100))

        all_sprites.draw(pygame.display.get_surface())
        for image in all_images:
            image.blit()

    def update_handler(self,dt):
        all_sprites.update(dt)
        for image in all_images:
            image.update(dt)




