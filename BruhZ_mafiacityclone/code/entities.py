"""
entities like npc, player etc. thinking for themself
"""



import pygame
from helpers import *
from pygame.math import Vector2 as vector
from settings import *
from Autoload import *



class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.life = 100
        self.arm_pos = vector()
    def update(self,dt): pass

    def took_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.kill() #pozniej sie to zmieni

class Player(Entity):
    def __init__(self ,start_pos):
        super().__init__()
        hurtbox_sprites.add(self)

        self.scale = 3
        self.sprite = pygame.image.load("../images/white_cj.png")
        self.sprite = pygame.transform.scale(self.sprite, \
                                             (self.sprite.get_width()*self.scale,self.sprite.get_height()*self.scale))

        #main variables
        self.pos = start_pos
        self.image = self.sprite
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect(center = self.pos)


        #rectangle for collision with objects
    #local position on image of topleft rectange
        self.obj_c_pos = vector(5 * self.scale,21* self.scale)
    #local size on image of topleft rect plus self.obj c pos
        self.obj_c_size = vector(6* self.scale,8* self.scale)
        self.obj_c_rect = pygame.Rect(self.obj_c_pos[0],self.obj_c_pos[1],self.obj_c_size[0],self.obj_c_size[1])

        #move var
        self.inputvec = vector()
        self.movvec = vector()
        self.walk_acceleration = 30
        self.walk_speed = 170

        #group variables
        self.coll_sprites = collide_sprites
        self.obj_sprites = object_sprites

        self.hurtbox_pos = vector(4 * self.scale, 13 * self.scale)
        self.hurtbox_size = vector(8 * self.scale, 14 * self.scale)
        self.hurtbox_rect = pygame.Rect(self.hurtbox_pos[0], self.hurtbox_pos[1], self.hurtbox_size[0], self.hurtbox_size[1])

        #weapons and inventory
        self.inventory = {
            'oneHand': None,        #0
            'twoHand': None,        #1

        }
        self.choosen_weap = 1

        #arm for testing
        self.arm_lenght = 20
        self.arm_angle = 0

        #for input variables
        self.shoot = False
        self.reload =False
        self.put_down = False


    def weapon_handling(self):
        for i,weapon in enumerate(self.inventory.values()):
            if weapon != None:
                if i == self.choosen_weap:
                    weapon.active = True
                    if self.shoot:
                        weapon.shoot = True
                    elif self.reload:
                        weapon.reload()
                    elif self.put_down:
                        weapon.put_down(self.rect.center)
                        for tuples in self.inventory.items():
                            self.inventory[tuples[0]] = None
                else:
                    weapon.active = False

    def input(self):
        #x y movement input
        self.inputvec.x = inputHandler(pg.K_d) - inputHandler(pg.K_a)
        self.inputvec.y = inputHandler(pg.K_s) - inputHandler(pg.K_w)
        if self.inputvec != vector(): self.inputvec = self.inputvec.normalize()

        #interact input and other
        self.interact = inputHandler(pg.K_e) #interact with obj
        self.shoot = mouse_input_handler((1,0,0))
        self.reload = inputHandler(pg.K_r)
        self.put_down = inputHandler(pg.K_q)

        if inputHandler(pg.K_1):self.choosen_weap =0
        elif inputHandler(pg.K_2): self.choosen_weap = 1

    def arm(self):
        #calculating the end of arm pos
        x,y =pygame.mouse.get_pos()[0] - self.rect.centerx , \
                              pygame.mouse.get_pos()[1] - self.rect.centery

        self.arm_pos = vector(x,y).normalize() if (x,y) != (0,0) else vector()
        self.arm_angle = angle_of_vector(self.arm_pos)  # cant be arm pos
        self.arm_pos = vector(self.rect.centerx + self.arm_pos[0]* self.arm_lenght,\
                              self.rect.centery + self.arm_pos[1]* self.arm_lenght)

    def move_collision(self,direction):
        #collision with walls etc
        for sprite in self.coll_sprites:
            if getattr(sprite,"collideable") and self.rect.colliderect(sprite):
                if direction == "vertical":
                    if self.movvec.x >= 0: # prawo
                        self.rect.right = sprite.rect.left
                    elif self.movvec.x <= 0:  # lewo
                        self.rect.left = sprite.rect.right
                elif direction == "horizontal":
                    if self.movvec.y >= 0:  # dol
                        self.rect.bottom = sprite.rect.top
                    elif self.movvec.y <= 0:  # gora
                        self.rect.top = sprite.rect.bottom

    def object_collision(self):
        #collision with objects and interacting
        objects_list = []
        for object in self.obj_sprites:
            if self.obj_c_rect.colliderect(object.rect) and self.interact:
                for tuples in self.inventory.items():
                    if str(object.weapon_type) == str(tuples[0]) and self.inventory[tuples[0]] ==None:
                        objects_list.append(object)
        if objects_list != []:
            objects_list[0].interact(self)

    def movement(self,dt):
        self.movvec.x = move_towards(self.movvec.x, self.walk_acceleration *dt, self.inputvec.x * self.walk_speed*dt)
        self.movvec.y = move_towards(self.movvec.y, self.walk_acceleration *dt, self.inputvec.y * self.walk_speed*dt)

        self.rect.centerx += int(self.movvec.x )
        self.move_collision("vertical")
        self.rect.centery += int(self.movvec.y )
        self.move_collision("horizontal")

    def update(self,dt):
        self.movement(dt)
        self.object_collision()
        self.arm()
        self.weapon_handling()

        self.obj_c_rect.topleft = self.rect.topleft + self.obj_c_pos
        self.hurtbox_rect.topleft = self.rect.topleft + self.hurtbox_pos



class NPC_Basic(Entity):
    def __init__(self,start_pos):
        super().__init__()
        hurtbox_sprites.add(self)

        self.scale = 3
        self.sprite = pygame.image.load('../images/npc.png')
        self.sprite = pygame.transform.scale(self.sprite,\
                                             (self.sprite.get_width() *self.scale, self.sprite.get_height() *self.scale))
        #main variables
        self.image = self.sprite
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect(center = start_pos)

        self.hurtbox_pos = vector(4 * self.scale, 13 * self.scale)
        self.hurtbox_size = vector(8 * self.scale, 14 * self.scale)
        self.hurtbox_rect = pygame.Rect(self.hurtbox_pos[0], self.hurtbox_pos[1], self.hurtbox_size[0], self.hurtbox_size[1])

    def update(self,dt):
        self.hurtbox_rect.topleft = self.rect.topleft + self.hurtbox_pos