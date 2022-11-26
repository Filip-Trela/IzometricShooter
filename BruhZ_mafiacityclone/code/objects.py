"""
objects that can be picked up, like weapons, probably only weapons
"""

import pygame
from Autoload import *
from pygame.math import Vector2 as vector
from helpers import *
import random

class Object(pygame.sprite.Sprite): #a sprite class for all sprites group
    def __init__(self, start_pos, sprite = pygame.image.load("../images/gun.png"), scale = 2):
        super().__init__([all_sprites,object_sprites] )

        # main variables
        self.pos = start_pos

        self.sprite = sprite
        self.sprite.set_colorkey((255, 255, 255))
        x,y = self.sprite.get_size()
        self.image = pygame.transform.scale(self.sprite, (x * scale, y * scale))

        self.rect = self.image.get_rect(topleft = self.pos)

    def interact(self, byWho):
        #byWho is like interacted by player
        pass

    def blit(self):
        pygame.display.get_surface().blit(self.image, self.pos,)


class Obj_Image: #just an image class
    def __init__(self,position):
        self.pos = position
        all_images.append(self)

        #behaviour control variables?
        self.active = True

        #visualization part
        self.sprite = pygame.image.load("../images/gun.png")
        self.sprite.set_colorkey((255,255,255))
        self.scale = 2
        self.image = pygame.transform.scale(self.sprite, (self.sprite.get_width()*self.scale,\
                                                          self.sprite.get_height()*self.scale))
        self.img_size_half = self.image.get_rect().center

    def blit(self):
        if self.active:
            pygame.display.get_surface().blit(self.image, self.pos - self.image.get_rect().center,)

    def update(self,dt):
        if self.active: self.updating_logic(dt)

    def updating_logic(self,dt):
        pass

    def kill(self):
        for num, image in enumerate(all_images):
            if self is image:
                #removes the obj from group
                all_images.pop(num)





class GunBlueprint(Obj_Image):
    """
            attributes that you should care:
             muzzlex\y , range, magazine_size, automatic, milisec_between, milisec_reload, shoot_color,
             shoot_width, scale, sprite

             other notes:
             - center of rotation should be in center of your image, do your image like that
             - robiac nowa bron, operator w super init bez self.arm_pos
    """
    def __init__(self,
                 operator =None,
                 muzzle_x = 6,
                 muzzle_y= -2,
                 shot_range = 500,
                 magazine_size  = 6,
                 ammunition_in_clip = 0,
                 automatic = False,
                 milisec_between= 500,
                 milisec_reload= 2000,
                 shoot_color= (255,246,65),
                 shoot_width= 3,
                 scale= 2,
                 sprite= pygame.image.load("../images/gun.png"),
                 rotate_speed = 500,
                 knockback = [-100,-80,80,100],
                 damage = [60,120]
                 ):

        super().__init__(operator.arm_pos)
        self.putable_obj = ToPickGunBlueprint
        self.operator = operator

        self.scale = scale
        self.image = pygame.transform.scale(sprite, (int(sprite.get_width()*self.scale),\
                                                          int(sprite.get_height()*self.scale)))
        self.org_image = self.image

        self.gun_angle = self.operator.arm_angle
        self.rotate_speed = rotate_speed
        self.knockback = knockback

        self.muzzle_x = muzzle_x
        self.muzzle_y = muzzle_y
        self.muzzle_pos = vector(int(self.muzzle_x * self.scale), int(self.muzzle_y * self.scale))
        self.muzzle_pos_global = vector()
        self.raycast_line = ((),())
        self.range = shot_range

        self.start_ray_vis  = vector()
        self.end_ray_vis = vector()
        self.shoot_position = vector()

        self.shoot_color = shoot_color
        self.shoot_width = shoot_width
        self.affter_effect_fps = 2 #for delta, can be 1 or 2
        self.affter_effect_now = 0
        self.magazine_size = magazine_size
        self.mag_now_size = ammunition_in_clip
        self.automatic = automatic
        self.shoot = False
        self.key_down = 0
        self.damage = damage

        #timers
        self.milisec_between = milisec_between
        self.milisec_reload = milisec_reload
        self.timer_betw_shoots = Timer( self.milisec_between, func = None)
        self.timer_reload = Timer( self.milisec_reload, self.reloaded)

    def gun_angle_looking_at(self,dt):
        # cala lewa polowa
        if 90<self.operator.arm_angle<270:
            self.gun_angle = move_towards(self.gun_angle, self.rotate_speed *dt , self.operator.arm_angle)

            #real w dolnej prawej, rzeczywisty w gornej prawej
        elif 0<self.gun_angle<90 and 270<self.operator.arm_angle<360:
            self.gun_angle -= self.rotate_speed *dt
            if self.gun_angle <= 0:
                self.gun_angle += 359
            # real w gornej prawej, rzeczywisty w dolnej prawej
        elif 270<self.gun_angle<360 and 0<self.operator.arm_angle<90:
            self.gun_angle += self.rotate_speed *dt
            if self.gun_angle >= 359:
                self.gun_angle -= 359
        else:
            self.gun_angle = move_towards(self.gun_angle, self.rotate_speed*dt, self.operator.arm_angle)

    def set_image(self):
        self.image = pygame.Surface((SCREEN_SIZE[0]*2,SCREEN_SIZE[1]*2))
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((255, 255, 255))
        self.img_size_half = self.image.get_rect().center

#based on angle
    def flip_rotate_img(self):
        # flipping the image when is at the left side and important positions
        if 90 < self.operator.arm_angle < 270:
            self.rotated_img = pygame.transform.rotate(pygame.transform.flip(self.org_image, 0, 1), \
                                                       self.gun_angle)
            self.muzzle_pos = vector(int(self.muzzle_x * self.scale), int(-self.muzzle_y * self.scale))
        else:
            self.rotated_img = pygame.transform.rotate(self.org_image, self.gun_angle)
            self.muzzle_pos = vector(int(self.muzzle_x * self.scale), int(self.muzzle_y * self.scale))

        # sposob aby image krecil sie w miejscu, glownie chodzi o jego pozycje
        """ srodkowa pozycja obroconego image'a jest rowna srodkowi pozycji plaszczyzny"""
        return self.rotated_img.get_rect(
            center=self.org_image.get_rect(center=(self.image.get_rect().center)).center)

    def muzzle_pos_handler(self):

    #for physics
        # setting position of muzzle in global world
        self.muzzle_pos_global = self.pos + self.muzzle_pos.rotate(-self.gun_angle)
        # settings start and end of line
        self.raycast_line = (self.muzzle_pos_global, \
                             self.muzzle_pos_global + vector(self.range, 0).rotate(-self.gun_angle))

    #for visualization (done)
        self.muzzle_pos_local = self.muzzle_pos.rotate(-self.gun_angle) +\
                                vector(self.image.get_rect().width/2,self.image.get_rect().height/2)

        self.raycast_line_local =(self.muzzle_pos_local, \
             self.muzzle_pos_local + vector(self.range, 0).rotate(-self.gun_angle) )

    def raycasting(self):
        clipped = ()
        tries_colls = ()
        colls_list = []
        tries_hurts = ()
        hurts_list = []
        for colls in collide_sprites:
            #physics part
            #i know i should type trials but tries is for
        #tries collision for all objects, tries can equall ((x,y)(x,y)) or ()
            tries_colls = colls.rect.clipline(self.raycast_line[0][0],self.raycast_line[0][1],\
                                    self.raycast_line[1][0],self.raycast_line[1][1])
            colls_list.append(tries_colls)

        for hurts in hurtbox_sprites:
            # physics part
            # i know i should type trials but tries is for
            # tries collision for all objects, tries can equall ((x,y)(x,y)) or ()
            if hurts != self.operator: #jesli sam w siebie nie strzela
                tries_hurts = hurts.hurtbox_rect.clipline(self.raycast_line[0][0], self.raycast_line[0][1], \
                                               self.raycast_line[1][0], self.raycast_line[1][1])
            #take damage
                if tries_hurts != ():
                    hurts.took_damage(random.randint(self.damage[0],self.damage[1]))
            hurts_list.append(tries_hurts)

        #if anything been hitted
        for tries in hurts_list + colls_list:
            if tries != ():clipped = tries

        #visualization part
        self.start_ray_vis = self.raycast_line_local[0]
        if clipped != ():
            self.end_ray_vis = clipped[0] - self.raycast_line[0] + self.muzzle_pos_local
        else: self.end_ray_vis = self.raycast_line_local[1]

        #visualization of aiming, this part need to be in other func
        self.affter_effect_now =self.affter_effect_fps
        self.shoot_position = self.image.get_rect().center

    def visualization_of_bullet(self):
        if self.affter_effect_now >0:
            self.affter_effect_now -=1
            pygame.draw.line(self.image, self.shoot_color,\
                             self.start_ray_vis  ,self.end_ray_vis ,self.shoot_width)

    def reload(self):
        if self.mag_now_size != self.magazine_size and self.timer_reload.active == False:
            self.mag_now_size = 0
            self.timer_reload.activate()

    def reloaded(self):
        self.mag_now_size = self.magazine_size

    def shooting(self):
            # if gun is repetetive
        if not self.automatic:
            if self.shoot:
                if self.key_down == 0:
                    self.key_down = 1
                    if self.shoot and self.mag_now_size and self.timer_betw_shoots.active == False:
                        self.timer_betw_shoots.activate()
                        self.mag_now_size -=1
                        self.raycasting()
                        self.gun_angle += random.choice(self.knockback)

            elif not self.shoot: self.key_down = 0
            self.shoot = False

            #if gun is automatic
        else:
            if self.shoot and self.mag_now_size and self.timer_betw_shoots.active == False:
                self.key_down = 1
                self.timer_betw_shoots.activate()
                self.mag_now_size -=1
                self.raycasting()
                self.gun_angle += random.randint(self.knockback[0], self.knockback[1])
            self.shoot = False

    def put_down(self, position):
        self.putable_obj(vector(position) - vector(self.org_image.get_size())/2, ammunition_in_clip= self.mag_now_size)
        self.kill()

    def updating_logic(self,dt):
        #reseting a surface
        self.set_image()
        self.pos = self.operator.arm_pos
        self.gun_angle_looking_at(dt)
        new_rect = self.flip_rotate_img()
        self.muzzle_pos_handler()

        if dt* 10 >= 0.2:
            self.affter_effect_fps =1
        else: self.after_effect_fps = 2
        self.shooting()
        self.visualization_of_bullet()

        self.image.blit(self.rotated_img, new_rect)

        self.timer_betw_shoots.update()
        self.timer_reload.once_func_update()

        #print(self.mag_now_size)

class ToPickGunBlueprint(Object):
    """
    attributes that you should care:
             start position ,gun without Parentheses (as an object image),
             sprite that need to be hand set, weapon_type(one hand two hand etc)
    """
    def __init__(self,
                 start_pos,
                 gun= GunBlueprint,
                 sprite= pygame.image.load("../images/gun.png"),
                 scale= 2,
                 weapon_type = 'oneHand',
                 ammunition_in_clip = 6
                 ):

        self.gun = gun
        self.sprite = sprite
        self.scale = scale
        self.weapon_type = weapon_type
        self.ammo_in_clip = ammunition_in_clip
        super().__init__((start_pos), self.sprite, self.scale)



    def interact(self, byWho):
        for num, key in enumerate(byWho.inventory.keys()):
            if key == self.weapon_type and hasattr(byWho, 'arm_pos'):
                byWho.inventory[self.weapon_type] = self.gun(byWho, ammunition_in_clip= self.ammo_in_clip) #tu bedzie image object z parametrami
                self.kill()





class Revolver(GunBlueprint):
    def __init__(self,operator, ammunition_in_clip):
        super().__init__(operator,ammunition_in_clip=ammunition_in_clip)
        self.putable_obj = ToPickGunBlueprint #very important

class ToPickRevolver(ToPickGunBlueprint):
    def __init__(self, position):
        self.sprite = pygame.image.load("../images/gun.png")

        super().__init__(position,
        gun = Revolver,
        sprite = self.sprite,
        scale = 2,
        )




class FastGun(GunBlueprint):
    def __init__(self,operator, ammunition_in_clip):
        super().__init__(operator,ammunition_in_clip=ammunition_in_clip,
                         muzzle_x=6,
                         muzzle_y=-2,
                         shot_range=700,
                         magazine_size=30,
                         automatic=True,
                         milisec_between=100,
                         milisec_reload=3500,
                         shoot_color=(255, 246, 65),
                         shoot_width=2,
                         scale=2,
                         sprite=pygame.image.load('../images/automatic_gun.png'),
                         rotate_speed=400,
                         knockback=[-30, -10, 10, 30],
                         damage=[60, 70]
                         )
        self.putable_obj = ToPickFastGun #very important


class ToPickFastGun(ToPickGunBlueprint):
    def __init__(self, position):
        self.sprite = pygame.image.load('../images/automatic_gun.png')

        super().__init__(position,
        gun = FastGun,
        sprite = self.sprite,
        scale = 2,
        weapon_type='twoHand'
        )