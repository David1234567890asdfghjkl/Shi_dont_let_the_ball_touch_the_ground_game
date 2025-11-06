#created by David Shi
#Sprite Module
#sprites: mob, player
import pygame as pg
import random
from pygame.sprite import Sprite
from settings import *
from utils import *
import math
import random
vec = pg.math.Vector2
#draw circle
    #https://www.pygame.org/docs/ref/draw.html#pygame.draw.circle
#thanks to copilot for ring stuff

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        #drawing player
        self.dead = False
        self.game = game
        self.image = self.game.player_img
        #make image the player png
        self.rect = self.image.get_rect()
        #movement attributes
        #speed is speed change each tick when ad keys pressed
        self.speed = 1
        self.vel=vec(0,0)
        self.pos=vec(x,y)
        #max horizontal_speed, movement key in same direction will no longer accelerate
        self.max_horizontal_speed = 8
        #amount vel x will decrease when keys not touched
        self.deaccel = 0.5
        #how many double jumps player will get when touching floor
        self.extra_jumps = 2
        #how many double jumps player currently has
        self.jumps = 2
        #cooldown so jump doesnt trigger multiple times when w pressed to prevent double jumping 
        self.jump_cd = Cooldown(420)

        #how close player has to be to ball to kick
        self.range = 40
        #when kicked, how fast hte ball will go
        self.kick_force = 12
        #jump power
        self.jump_power = 17
        self.cd = Cooldown(150)

        self.ring = Ring(self.game, self, self.range)
        #time that ring will flash when successfully kicking
        self.hitflash = Cooldown(150)

    def jump(self):
        print(self.jumps)
        #if touching ground, jump, jump sets vel y to a predetermined value
        #teleport down to check if on ground because when on the ground, player floats above the ground due to collision
        self.rect.y += GRAVITY
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        self.rect.y -= GRAVITY
        #reverse teleportation so it doesnt conflict with the wall collide function
        if hits:
            if self.jump_cd.ready():
                #start jump cooldown so player waits before w triggers jump again
                self.jump_cd.start()

                self.vel.y = -self.jump_power
                #is touching floor so reset double jumps amount
                self.jumps = self.extra_jumps
            #if player has double jumps jump and subtract a jump

        elif self.jumps > 0:
            if self.jump_cd.ready():
                #start jump cooldown so player waits before w triggers jump again
                self.jump_cd.start()

                self.jumps -=1
                self.vel.y = -self.jump_power
    

    def get_keys(self):
        #gravity acceleration
        self.vel.y += GRAVITY
        #movement based on wasd presses
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            #jump when w presed
            self.jump()

        if keys[pg.K_a]:
            if self.vel.x > -self.max_horizontal_speed:
                #if speed to the left hasnt reached max speed, accelerate to the left
                self.vel.x -= self.speed
            else:
                # if velocity surpassed max speed, set to max speed
                self.vel.x = -self.max_horizontal_speed
        elif self.vel.x < 0:
            self.vel.x += self.deaccel

        if keys[pg.K_d]:
            #d press same as a press but inversed
            if self.vel.x < self.max_horizontal_speed:
                self.vel.x += self.speed
            else:
                self.vel.x = self.max_horizontal_speed
        elif self.vel.x > 0:
            self.vel.x -= self.deaccel
   
        #push ball if space pressed.
        if keys[pg.K_SPACE]:
            #kick if the ball is close enough
            #update balls color, white if not kicking, red if kick but missed, blue is hit
            if calculatedist(self.rect.center,self.game.ball.rect.center)<self.range or calculatedist(self.rect.center,self.game.ball.rect.center) == self.range:
                self.kick()
                #start timer so ring can flash blue until done
                self.hitflash.start()
                self.ring.color = BLUE
            elif self.hitflash.ready():
                self.ring.color = RED
        elif self.hitflash.ready():
            self.ring.color = WHITE

    def kick(self):

        #get direction to kick the ball by getting the difference between coords of player and ball
            #kick ball in direction directly away from player
        direction = vec(self.rect.center)-vec(self.game.ball.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()
        #slope of line pointing to ball
        #direction vector multiplied by kick force scalar
        self.game.ball.vel = direction * -self.kick_force

    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            #check what we hit and according
            if str(hits[0].__class__.__name__) == "Mob":
                if self.cd.ready():
                    if not self.game.win:
                        self.health -= 2
                    self.cd.start()
                #if health is 0
                if self.health <= 0:
                    self.dead = True
                    self.health = 0
                #immunity time
    
    #collision with walls
    #dont move if going through wall
    def collide_with_walls(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits:
            if dir == 'x':
                if hits[0].state == "movable":
                    #move wall in direction of player movement
                        #movement is slowed when movinga  wall
                    hits[0].vel.x = self.vel.x
                else:
                    if self.vel.x > 0:
                        self.pos.x = hits[0].rect.left - self.rect.width
                    if self.vel.x < 0:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
            if dir == 'y':

                if hits[0].state == "movable":
                    #move wall in direction of player movements
                    hits[0].vel.y = self.vel.y
                else:
                    if self.vel.y > 0:
                        self.pos.y = hits[0].rect.top - self.rect.height
                    if self.vel.y < 0:
                        self.pos.y = hits[0].rect.bottom
                    self.vel.y = 0
                    self.rect.y = self.pos.y

    def update(self):
        #get key presses
        self.get_keys()
        #only move if not dead
        if not self.dead:
            self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        #check for collisions with mobs
        self.collide_with_stuff(self.game.all_mobs, False)

#RING to attach to the player to indicate the area in which the player can kick the ball
class Ring(Sprite):
    def __init__(self,game, player, radius):
        self.groups = game.all_sprites
        Sprite.__init__(self,self.groups)
        self.player = player
        self.game = game
        self.radius = radius
        self.diameter = self.radius*2
        self.pos = self.player.pos
        self.color = WHITE
        self.image = pg.Surface((self.diameter,self.diameter), pg.SRCALPHA)
        # Draw hollow circle
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 1)
        #rect of sprite surface
        self.rect = self.image.get_rect()



    def update(self):
        self.pos = vec(edit_center(self.rect, self.player.rect.center))
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        #redraw image so it can update
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 1)
        
class Mob(Sprite):
    def __init__(self, game, x, y,color):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.color = color
        self.image = pg.Surface((11, 8))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x*TILESIZE[0]
        self.rect.y = y*TILESIZE[1]
        self.speed = 3
        self.vel = vec(self.speed*random.choice([1,-1]),self.speed*random.choice([1,-1]))
        self.pos= vec(x* TILESIZE[0],y* TILESIZE[1])
        self.collide = [0,0]
        self.colliding = False

    def collide_with_walls(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits:
            self.colliding = True

            if dir == 'x':
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
            if dir == 'y':
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.rect.y = self.pos.y
        else:
            self.colliding = False

    def collide_with_stuff(self, group):
        hits = pg.sprite.spritecollide(self, group, False)
        if hits: 
            #check what we hit and according
            if str(hits[0].__class__.__name__) == "Wall":
                #if hit a wall bounce
                self.speed*=-1

    def update(self):
        self.pos.x += self.vel.x
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        #bounce off walls in direction of player
        #self.colliding is if we hit a wall and is found from self.collide_with_walls)()
        if self.colliding:
            self.vel.x *= -1
            if self.pos.y < self.game.player.pos.y:
                self.vel.y = self.speed
            else:
                self.vel.y = -self.speed

        self.rect.y = self.pos.y
        self.pos.y += self.vel.y
        self.collide_with_walls('y')
        if self.colliding:
            self.vel.y *= -1
            if self.pos.x < self.game.player.pos.x:
                self.vel.x = self.speed
            else:
                self.vel.x = -self.speed

class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.vel= vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.game = game
        self.groups = game.all_sprites
        self.image = pg.Surface(TILESIZE)
        self.value = random.randint(50,140)
        self.image.fill((self.value,self.value,self.value))
        self.rect = self.image.get_rect()
        #[0] is width, [1] is height
        self.rect.x = x*TILESIZE[0]
        self.rect.y = y*TILESIZE[1]
        self.state = "immovable"

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.vel.x =0
        self.vel.y =0

class Ball(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        #gravity multiplier so it falls slower
        self.gravitymultiplier = 0.4
        #dimensions and characteristics
        self.radius = 8
        self.diameter = int(self.radius*2)
        self.color = WHITE
        #vertical deacceleration due to air resistance vertical is too annoing
            #y_decrease = drag coefficient * speed
        self.drag_multiplier = 0.02
        #terminal velocity is maximum downward speed
        self.terminal_velocity = 3
        #velocity
        self.vel = vec(0,0)
        #position(not actual rect pos)
        self.pos = vec(x,y)
        #ball image
        #SRCALPHA to make the surface not fill black
        self.image = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        #draw circle on image surface
        pg.draw.circle(self.image, WHITE, (self.radius,self.radius), self.radius)
        #rect of sprite surface
        self.rect = self.image.get_rect()

    def update(self):
        #gravity force
        # if not touching a floor gravity will negatively accelerate
        self.vel.y += GRAVITY*self.gravitymultiplier
        #air resistance decreases speed
        self.vel.x -= self.drag_multiplier*self.vel.x
        #if horizontal speed is close enough to zero, become zero since air resistance approaches 0 and never reaches
        if abs(self.vel.x) < 0.5:
            self.vel.x = 0
        #update position var based on velocity
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        #update rect position based on pos var
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        #bounce off left and right wall, reverse vel x
        if self.rect.right == WIDTH or self.rect.right > WIDTH:
            #set rect.right to the border to avoid ball going too far out and repeatedly reversing direction
            self.rect.right = WIDTH
            #reverse vel.x to bounce
            self.vel.x = -self.vel.x
        elif self.rect.left == 0 or self.rect.left <0:
            self.rect.left = 0
            self.vel.x = -self.vel.x