#created by David Shi
#Sprite Module
#sprites: mob, player
import pygame as pg
import random
from pygame.sprite import Sprite
from settings import *
from utils import *
import math
vec = pg.math.Vector2
#draw circle
    #https://www.pygame.org/docs/ref/draw.html#pygame.draw.circle
#thanks to copilot for ring stuff

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        #drawing player
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
        self.max_horizontal_speed = 11
        self.max_fall_speed = 26
        #amount vel x will decrease when keys not touched
        self.deaccel = 0.5
        #how many double jumps player will get when touching floor
        self.extra_jumps = 3
        #how many double jumps player currently has
        self.jumps = self.extra_jumps
        #cooldown so jump doesnt trigger multiple times when w pressed to prevent double jumping 
        self.jump_cd = Cooldown(420)
        #jump power
        self.jump_power = 19
        #velocity increase from pressing lshift to fall slower
        self.float_speed = 0.3
        #fastest vertical speed if floating via lshift
        self.max_float_speed = 5
        #velocity decrease pressing s to fall faster gives
        self.fall_speed = 0.7
        #how close player has to be to  to kick
        self.range = 40
        #create ring around player
        self.ring = Ring(self.game, self, self.range)
        #increase range so player can kick ball even if the ball is touching the ring but the balls center is not close
        self.range = self.range + self.game.ball.radius
        #when kicked, how fast hte ball will go
        self.kick_force = 12
        self.cd = Cooldown(150)
        #is player touching ground
        self.touching_ground = False
        #time that ring will flash when successfully kicking
        self.hitflash = Cooldown(150)

    def jump(self):
        if self.touching_ground == True:
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
        #CONTROLS
        #w jump
        #ad left and right
        #space to kick the ball
        #lshift to fall slower
        #s to fall faster

        #gravity acceleration if not reached max fall speed
        if self.vel.y < self.max_fall_speed:
            self.vel.y += GRAVITY
        else:
            self.vel.y = self.max_fall_speed
        #movement based on wasd presses
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            #jump when w presed
            self.jump()
        #holding l shift makes player fall slower and enforces slower max vertical speed
        if keys[pg.K_LSHIFT]:
            if self.touching_ground == False and self.vel.y>0:
                self.vel.y -= self.float_speed
                if self.vel.y > self.max_float_speed:
                    self.vel.y = self.max_float_speed

        #s key makes player fall faster via extra acceleration
        if keys[pg.K_s]:
            if self.touching_ground == False:
                self.vel.y += self.fall_speed
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
            #update balls color, white if not kicking, red if kick but missed, blue is hit, green if ball can be hit(overrides blue) but code is elsewhere
            if calculatedist(self.rect.center,self.game.ball.rect.center)<self.range or calculatedist(self.rect.center,self.game.ball.rect.center) == self.range:
                self.game.vineboom_sound.play()
                kick(self,self.game.ball,self.kick_force)
                #start timer so ring can flash blue until done
                self.hitflash.start()
                self.ring.color = BLUE
            elif self.hitflash.ready():
                self.ring.color = RED
        elif self.hitflash.ready():
            self.ring.color = WHITE
    
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
        #check if ball is on gorund
        #teleport down to check if on ground because when on the ground, player floats above the ground due to collision
        self.rect.y += GRAVITY
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        self.rect.y -= GRAVITY
        #reverse teleportation so it doesnt conflict with the wall collide function
        if hits:
            self.touching_ground = True
        else:
            self.touching_ground = False
        #get key presses
        self.get_keys()
        #only move if not dead
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        #if player can hit ball, flash green
        if calculatedist(self.rect.center,self.game.ball.rect.center)<self.range or calculatedist(self.rect.center,self.game.ball.rect.center) == self.range:
            self.ring.color = GREEN

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
        self.rect.center = self.player.rect.center
        #redraw image so it can update
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 1)

class Ball(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_balls
        Sprite.__init__(self, self.groups)
        self.game = game
        #gravity multiplier so it falls slower
        self.gravitymultiplier = 0.35
        #dimensions and characteristics
        self.radius = 8
        self.diameter = int(self.radius*2)
        self.color = WHITE
        #vertical deacceleration due to air resistance vertical is too annoing
            #y_decrease = drag coefficient * speed
        self.drag_multiplier = 0.02
        #terminal velocity is maximum downward speed
        self.terminal_velocity = 2.5
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
        #what y coord constitutes the ground
        self.ground = HEIGHT - 64

    #centralized collision for the objects and the ball (only the objects that collide based off rectanagular shape)
        #for when the object rams into the ball instead of the ball running into the object
    def collided_by_stuff(self):
        #collide is whether a collision is sensed for that axis
        xcollide = False
        ycollide = False
        #hit is whether it decides to actually kick the ball or do nothing
        xhit = False
        yhit = False
    # used copilot and the github copilto quite a bit to debug collision interactions
        hits = pg.sprite.spritecollide(self, self.game.all_colliding_objects, False)
        if hits:
            pg.mixer.Sound.play(self.game.ding_sound)
            #store hits[0] because another spritecollide is coming
            hit = hits[0]

            if hit.vel.x != 0:
                #changing rect position of hit's by reversing velocity to see if its x speed caused the collision
                hit.rect.x -= hit.vel.x
                hits = pg.sprite.spritecollide(self, self.game.all_colliding_objects, False)
                hit.rect.x += hit.vel.x
                #if reversing the velocity for that tick didnt cause the collision, it didn't bump into the ball from that direction
                if not hits:
                    #check what direction the collider is traveling to change ball vel accordingly
                    xcollide = True

            if hit.vel.y != 0:
                hit.rect.y -= hit.vel.y
                hits = pg.sprite.spritecollide(self, self.game.all_colliding_objects, False)
                hit.rect.y += hit.vel.y
                if not hits:
                    ycollide = True
            
            #if both xcollid and ycollide are true, decide to keep both or drop one 
                #this is because of clarity issues for when bouncers have ball collide with corners causing a perfectly diagonal ball velocity
                    #it makes more sense to choose one because ITS A RECTANGLE and the ball logically should only collide with one side
            if xcollide == True:
                xhit = True
            if ycollide == True:
                yhit = True
            #decide which to choose, choose the faster axis velocity
            if ycollide == True and xcollide == True:
                if abs(hit.vel.y) > abs(hit.vel.x):
                    xhit = False
                elif abs(hit.vel.x) > abs(hit.vel.y):
                    yhit = False
                #if both are equal do nothing because both axiss hit

            #if xhit is true, continue with x kick action and vice versa
            if xhit == True:
                if hit.vel.x > 0:
                    #only if objects speed is higher or else ball collided with object
                    if hit.vel.x > self.vel.x:
                        #change velocity
                        self.vel.x = hit.kick_force
                        #put ball at the edge of the edge at which they collided so they are no longer colliding
                        self.rect.left = hit.rect.right
                        #get self.pos in sync with self.rect
                        self.pos.x = self.rect.x
                else:
                    if hit.vel.x < self.vel.x:
                        self.vel.x = -hit.kick_force
                        self.rect.right = hit.rect.left
                        self.pos.x = self.rect.x
            #same as x for y
            if yhit == True:
                if hit.vel.y > 0:
                    if hit.vel.y > self.vel.y:
                        self.vel.y = hit.kick_force
                        self.rect.top = hit.rect.bottom
                        self.pos.y = self.rect.y
                else:
                    if hit.vel.y < self.vel.y:
                        self.vel.y = -hit.kick_force
                        self.rect.bottom = hit.rect.top
                        self.pos.y = self.rect.y

    #for when ball collides into an object because of balls velocity
    def collide_with_stuff(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.all_colliding_objects, False)
        #if collided with anything, reverse velocity and seperate the ball from the collide object
        if hits:
            pg.mixer.Sound.play(self.game.click_sound)
            if dir == 'x':
                #check what direction ball is moving to adjust velocity and position accordingly
                    #if colliding by ball going to the left, then the ball collided with the right side of the hit and vice versa
                if self.vel.x > 0:
                    #if the hit is going in the direction of player go the hits velocity x to the left to avoid more collision
                    if hits[0].vel.x < 0:
                        self.rect.right = hits[0].rect.left+hits[0].vel.x
                    else:
                        #go to edge of hit so not colliding anymore
                        self.rect.right = hits[0].rect.left

                if self.vel.x < 0:
                    if hits[0].vel.x > 0:
                        self.rect.left = hits[0].rect.right+hits[0].vel.x
                    else:
                        self.rect.left = hits[0].rect.right
        
            #reverse velocity
            self.vel.x *= -1
            #synce pos with rect
            self.pos.x = self.rect.x

            if dir == 'y':
                if self.vel.y > 0: 
                    if hits[0].vel.y<0:
                        self.rect.bottom = hits[0].rect.top+hits[0].vel.y
                    else:
                        self.rect.bottom = hits[0].rect.top

                if self.vel.y < 0:
                    if hits[0].vel.y>0:
                        self.rect.top = hits[0].rect.bottom+hits[0].vel.y
                    else:
                        self.rect.top = hits[0].rect.bottom
            self.vel.y *= -1
            self.pos.y = self.rect.y

    def dont_touch_ground(self):
        if self.rect.bottom == self.ground or self.rect.bottom > self.ground:
            self.game.lose = True
            self.game.playing = False

    def update(self):
        self.collided_by_stuff()
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
        
        self.rect.x = self.pos.x
        self.collide_with_stuff('x')
        self.rect.y = self.pos.y
        self.collide_with_stuff('y')

        #bounce off left and right wall, reverse vel x
        if self.rect.right == WIDTH or self.rect.right > WIDTH:
            #set rect.right to the border to avoid ball going too far out and repeatedly reversing direction
            self.rect.right = WIDTH
            self.pos.x = self.rect.x
            #reverse vel.x to bounce
            self.vel.x = -self.vel.x
        elif self.rect.left == 0 or self.rect.left <0:
            self.rect.left = 0
            self.pos.x = self.rect.x
            self.vel.x = -self.vel.x

        #bounce off top wall
        if self.rect.top == 0 or self.rect.top < 0:
            #set rect.right to the border to avoid ball going too far out and repeatedly reversing direction
            self.rect.top = 0
            self.pos.y = self.rect.y
            #reverse vel.y to bounce
            self.vel.y = -self.vel.y
        
        #check for lsoe condition
        self.dont_touch_ground()

class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.vel= vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.game = game
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
        self.vel.x = 0
        self.vel.y = 0

#bouncer bounces ball away when they touch
class Bouncer(Sprite):
    #random tells sprite whether it should generate at a random location, so x and y are optional
        #Copilot helped make x and y optional
    def __init__(self,game, randomspawn,x=67,y=67):
        self.groups = game.all_sprites, game.all_objects,game.all_colliding_objects
        Sprite.__init__(self, self.groups)
        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.game = game
        self.image = pg.Surface((34,34))
        self.rect = self.image.get_rect()
        self.kick_force = 10
        self.speed = 5
        #die after lifetimebounce BOUNCES
        self.lifetimebounces = 15
        # # of bounces left 
        self.bounces = self.lifetimebounces

        #if random is false spawn at given cords 
        if randomspawn == False:
            self.rect.x = x
            self.rect.y = y
        else:
            #teleport sprite to random in bound locations until it isnt touching a wall.
            self.rect.x = random.randint(self.image.get_width(),WIDTH-self.image.get_width())
            self.rect.y = random.randint(self.image.get_height(),HEIGHT-self.image.get_height())
            hits = pg.sprite.spritecollide(self,self.game.all_walls, False)
            while hits:
                self.rect.x = random.randint(self.image.get_width(),WIDTH-self.image.get_width())
                self.rect.y = random.randint(self.image.get_height(),HEIGHT-self.image.get_height())
                hits = pg.sprite.spritecollide(self,self.game.all_walls, False)
        #appear after suitable position is found
        self.pos = vec(self.rect.x, self.rect.y)
        self.color = BLUE
        self.image.fill((self.color))

        #set velocity in random direction
        while self.vel.x == 0 and self.vel.y == 0:
            self.vel = vec(random.randint(-100,100),random.randint(-100,100))
        self.vel = self.vel.normalize()
        self.vel = self.vel * self.speed

    def movement(self):
        # bounce off walls and screen borders
        #bouncing decreases lifetime by decreasing self.bounces

        #update x position based on velocity
        self.pos.x +=self.vel.x
        #sync rect with pos
        self.rect.x = self.pos.x
        #check for collision
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits:
            if self.vel.x > 0:
                #make collided edge rect edge to avoid collision again
                self.rect.right = hits[0].rect.left
            if self.vel.x < 0:
                self.rect.left = hits[0].rect.right

            #reverse tick's velocity to avoid further collision
            self.rect.x -=self.vel.x
            #sync pos with rect
            self.pos.x = self.rect.x
            #reverse velocity to bounce
            self.vel.x *=-1
            #decrease bounces left
            self.bounces -=1
            
        #same but for voliding with screen borders
        if self.rect.right > WIDTH:
            #add edge to rect to avoid collision
            self.rect.right = WIDTH
            self.rect.x-=self.vel.x
            self.pos.x = self.rect.x
            self.vel.x *=-1
            self.bounces-=1
        #same thing
        if self.rect.left < 0:
            self.rect.left = 0
            self.rect.x-=self.vel.x
            self.pos.x = self.rect.x
            self.vel.x *=-1
            self.bounces-=1

        #same but w/y
        self.pos.y += self.vel.y
        self.rect.y = self.pos.y
        
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits:
            if self.vel.y > 0:
                self.rect.bottom = hits[0].rect.top
            if self.vel.y < 0:
                self.rect.top = hits[0].rect.bottom
            self.rect.y -=self.vel.y
            self.pos.y = self.rect.y
            self.vel.y *=-1
            self.bounces-=1

        
        if self.rect.top< 0:
            self.rect.top = 0
            self.rect.y -= self.vel.y
            self.pos.y = self.rect.y
            self.vel.y *=-1
            self.bounces-=1
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.rect.y -= self.vel.y
            self.pos.y = self.rect.y
            self.vel.y *= -1
            self.bounces -= 1

    def update(self):
        self.movement()
        #die if run out of bounces
        if self.bounces <= 0:
            self.kill()
        #change color based on bounces left before dying
        self.color = gradient((self.lifetimebounces-self.bounces)/self.lifetimebounces,0,255,0,0,0,(self.lifetimebounces-self.bounces)/self.lifetimebounces,255,0)
        
        #check if any color values are out of range and will produce errors
            #kill if color will produce error
        color_valid = True
        for i in range(3):
            if self.color[i] < 0:
                color_valid = False
            if self.color[i] > 255:
                color_valid = False
                
        #fill so color updates
        if color_valid == True:
            self.image.fill(self.color)
        else:
            self.kill()

    #evil ball will follow the path of the ball
    #evilballpositioner creates a list with all the positions of the ball during its life
        #so when the evil ball starts updating which is after the positioner dies, it can go to the previous positions of the ball
class EvilBallPositioner(Sprite):
    def __init__(self,evilball,game,framedelay):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.eb = evilball

        #render circle
        #ball image
        self.radius = self.game.ball.radius
        self.diameter = self.radius*2
        self.color = PURPLE
        #SRCALPHA to make the surface not fill black
        self.image = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        pg.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)
        
        #go to the ball and form image to foreshadow the coming of the evilball
        self.pos = self.game.ball.pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        #framedelay is the delay by the evilball will follow the ball
        #it will be how long the positioner will be alive
        self.framedelay = framedelay
        #how many frames the sprite has been active
        self.framesalive = 0
        #list for positions of ball
        self.ballpositions = []

    def update(self):
        #every frame, it records the position of the 
        #thank you to github copilot for teaching me .copy() for vectors
        #+1 to prevent easy lineup for evil ball and ball
        self.ballpositions.append(vec(self.game.ball.pos.copy().x-(self.eb.radius-self.radius)+1, self.game.ball.pos.copy().y-(self.eb.radius-self.radius)+1))
        self.framesalive +=1
        if self.framesalive == self.framedelay:
            #pass on ball's position data to evilball
            self.eb.ballpositions = self.ballpositions
            self.eb.birth()
            self.kill()
#Evil ball sprite is a display that show a copy of the ball but pink
class EvilBallSprite(Sprite):
    def __init__(self, game, eb):
        self.eb = eb
        self.game = game
        self.groups = self.game.all_sprites, self.game.all_objects
        Sprite.__init__(self, self.groups)
        self.game = game
        self.radius = self.game.ball.radius
        self.diameter = self.radius*2
        self.color = PURPLE
        #ball image
        #SRCALPHA to make the surface not fill black
        self.image = pg.Surface((self.diameter,self.diameter), pg.SRCALPHA)
        self.rect = self.image.get_rect() 
        self.rect.center=self.eb.evilballpositioner.rect.center
        pg.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)

    def update(self):
        self.rect.center=self.eb.rect.center
        
class EvilBall(Sprite):
    def __init__(self, game):
        self.game = game
        self.radius = 13
        self.diameter = self.radius*2
        self.color = (140,0,140)
        self.pos = vec(67,67)
        self.kick_force = 7
        #ball image
        #SRCALPHA to make the surface not fill black
        self.image = pg.Surface((self.diameter,self.diameter), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        
        #how many frames the ball will delay when following the balls path
        self.framedelay = 32
        #list to track positions of ball, will be gotten from positioner when it dies
        self.ballpositions = []

        self.evilballpositioner = EvilBallPositioner(self,self.game,self.framedelay)
        #wait for positioner to get list of positions
        #draw hollow crcle
        #pg.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 1)   

    #function for starting to exist
    def birth(self):
        self.groups = self.game.all_sprites, self.game.all_objects
        Sprite.__init__(self, self.groups)
        #create image of purple ball
        self.evilballsprite = EvilBallSprite(self.game,self)

    def update(self):
        #go to position of ball framedelay frames ago
        self.pos.x = self.ballpositions[0].x
        self.pos.y = self.ballpositions[0].y
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        #+1 to prevent easy lineup for evil ball and ball
        self.ballpositions.append(vec(self.game.ball.pos.copy().x-(self.radius-self.game.ball.radius)+1,self.game.ball.pos.copy().y-(self.radius-self.game.ball.radius)+1))
        self.ballpositions.remove(self.ballpositions[0])

        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 1)

        #kick if touching ball
        hits = pg.sprite.spritecollide(self, self.game.all_balls,False)
        if hits:
            kick(self,self.game.ball, self.kick_force)

#explodes if doesnt touch ball
    #instant lose basically
class timebomb(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_objects
        Sprite.__init__(self, self.groups)
        self.game = game
        #dimensions and characteristics
        self.radius = 18
        self.diameter = int(self.radius*2)
        self.color = GREEN
        #SRCALPHA to make the surface not fill black
        self.image = pg.Surface((self.diameter, self.diameter), pg.SRCALPHA)
        pg.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)
        self.rect = self.image.get_rect()

        #kickforce for hwne it eplodes
        self.kick_force = 37

        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        #self.defused
        self.defused = False
        #play tick sounds
        pg.mixer.music.load(self.game.tick_sound)
        pg.mixer.music.play(loops=-1)
        #when bomb will blow up
            #if defused when bomb will dissapear
        self.timer = Cooldown(11000)
        self.timer.start()

        #cooldown for when to die after defused
        self.defused_timer = Cooldown(500)

    def explode(self):
        self.game.explosion_sound.play()
        self.explosion_particle = Explosion(self.game,self.rect.center[0],self.rect.center[1])
        kick(self.explosion_particle, self.game.ball, self.kick_force)
        pg.mixer_music.stop()
        pg.mixer_music.unload()
        self.game.play_theme()

    def update(self):
        #defuse and turn bluewhen touched by ball
        hits = pg.sprite.spritecollide(self,self.game.all_balls, False)
        if hits:
            pg.mixer_music.stop()
            pg.mixer_music.unload()
            self.game.play_theme()
            #play defuse sound
                #only once 
            if self.defused == False:
                pg.mixer.Sound.play(self.game.defuse_sound)
            self.color = BLUE
            self.defused = True
            #start defuse timer
            self.defused_timer.start()
        
        #only update bomb timer status and become redder if not defused
        if self.defused == False:    
            #when timer runs out explode and die
            if self.timer.ready():
                self.explode()
                self.kill()
            else:
                #as time passes make bomb reder
                #when 100% red time will have run out
                self.color = gradient((self.timer.timertime/self.timer.time),0,255,(self.timer.timertime/self.timer.time),255,0)
        else:
            if self.defused_timer.ready():
                self.kill()

        pg.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)
    
class Explosion(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.explosion_img
        #make image the explosion img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #the opacity the particle image starts with
        self.max_opacity = 100
        
        #to see how long the particle stays on screen
        self.timer = Cooldown(2167)
        self.timeleft = self.timer.time
        self.timer.start()

    def update(self):
        #copitlot helped with opacity
        #set timeleft
        self.timeleft = self.timer.time - self.timer.timertime
        #when timer runs out kill particle
        if self.timer.ready():
            self.kill()
        #lower opacity as time goes on
            #opacity will reach 0 when  timer finishes and particle dies
        self.image.set_alpha(self.max_opacity*(self.timeleft/self.timer.time))
        

#this class manages all spawning of enemy objects
class SpawnManager():
    def __init__(self,game):
        self.game = game

        #get time of creation
        self.start_time = pg.time.get_ticks()
        #how much time the spawnManager has been alive
        self.time_alive = pg.time.get_ticks() - self.start_time

        #max spawn chance is 0.5 of original chance
        self.max_spawn_chance = 0.6
        #some minutes to reach max spawn chance
        self.max_chance_time = 600000

        #chance of spawning a [blank] is 1 in [blank]_chance ticks
        self.Bouncer_chance = 13000
        self.Timebomb_chance = 12000
        
        #define spawns
        #will create the list of spawns
        self.define_spawns()

        #for spawning things once
        #[][0] is what to spawn
        #[][1] is arguments
        #[][2] is when to spawn
        #evil ball parameters are a list to make arguments iterable
        self.spawnonce_list = [[Bouncer,(self.game,True),1000],[timebomb, self.spawn_list[1][1],4000],[EvilBall,[self.game],24000]]
        #list of hasrun variables for spawnonce
        self.hasrun = []
        for i in range(len(self.spawnonce_list)):
            self.hasrun.append(False)

    #this list is to deifne all the spawns, it is a method so it can randomize te spawn locations
    def define_spawns(self):
        #list says all the sprites to spawn, each list is 
        #what to spawn
        #arguments
        #1/x chance of spawning(will not be mutabled)
        #1/x chance of spawning (will be mutabled)
        #after x ticks, it can spawn
        self.spawn_list = [[Bouncer,(self.game,True),self.Bouncer_chance,self.Bouncer_chance,0],[timebomb,(self.game, random.randint(20,WIDTH-20),random.randint(20,HEIGHT-230)),self.Timebomb_chance,self.Timebomb_chance, 10000]]


    def spawn(self):
        #update spawn list to randomize spawn locations
        self.define_spawns()

        self.time_alive = pg.time.get_ticks() - self.start_time
        #update time alive

        for i in range(len(self.spawn_list)):
            #self.spawn_list[i][2] is the original spawn chance
            #self.spawn_list[i][3] is the spawn chacne that will be updated
            #self.spawn_list[i][4] is the time after which the obejct can spawn
            ORIGINAL_SPAWN_CHANCE=self.spawn_list[i][2]
            spawn_chance = self.spawn_list[i][2]
            SPAWN_START_TIME = self.spawn_list[i][4]

            object = self.spawn_list[i][0]
            object_args = self.spawn_list[i][1]

            #check if enough time has passed to spawn object
            if self.time_alive > SPAWN_START_TIME:
                #spawn chance decreases over time and plateus
                if self.time_alive-SPAWN_START_TIME > self.max_chance_time:
                    spawn_chance = ORIGINAL_SPAWN_CHANCE*self.max_spawn_chance
                else:
                    #decrease spawn chance linearly over time
                    spawn_chance = linear((self.time_alive-SPAWN_START_TIME)/self.max_chance_time, ORIGINAL_SPAWN_CHANCE, ORIGINAL_SPAWN_CHANCE*self.max_spawn_chance)
                    self.spawn_list[i][3] = spawn_chance
                #1/[blank]_chance chance to spawn [blank]
                if random.randint(1,int(spawn_chance/FPS)) == 2:
                    #spawn the object
                    #github copilot helped with the unpacking of arguments
                    self.game.object = object(*object_args)

        self.spawnonce()

    def spawnonce(self):
        #check whether to spawn one time objects
        for i in range(len(self.spawnonce_list)):
            object = self.spawnonce_list[i][0]
            object_args = self.spawnonce_list[i][1]
            SPAWN_TIME = self.spawnonce_list[i][2]

            if self.time_alive > SPAWN_TIME and self.hasrun[i] == False:
                #spawn the object
                self.game.object = object(*object_args)
                self.hasrun[i] = True
        