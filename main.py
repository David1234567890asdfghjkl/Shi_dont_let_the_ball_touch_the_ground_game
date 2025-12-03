#Some code from https://bcpsj-my.sharepoint.com/personal/ccozort_bcp_org/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fccozort%5Fbcp%5Forg%2FDocuments%2FDocuments%2F000%5FComputer%5FProgramming%2F2025%5F2026%5FFall%2Fclass%5Fcode%2Fmy%5Fgame%2Fmain%2Epy&parent=%2Fpersonal%2Fccozort%5Fbcp%5Forg%2FDocuments%2FDocuments%2F000%5FComputer%5FProgramming%2F2025%5F2026%5FFall%2Fclass%5Fcode%2Fmy%5Fgame
#David Shi
#import necessary modules
#core game loop
#Input
#update
#draw
#yay ic an use github tform vs code
# importing the libraries to begin the code with proper values
import math
import random
import sys
import pygame as pg
from settings import *
from sprites import *
from utils import *
from os import path
import random
vec=pg.math.Vector2

pg.font.init()

class Game:
    def __init__(self):
      pg.init()
      pg.mixer.init()
      self.clock = pg.time.Clock()
      self.screen = pg.display.set_mode((WIDTH, HEIGHT))
      pg.display.set_caption("the  game")
      self.playing = True
      self.running = False
      self.lose = False

    def load_data(self):
        self.game_folder = path.dirname(__file__)
        self.img_folder = path.join(self.game_folder, 'images')
        self.snd_folder = path.join(self.game_folder, 'sounds')
        #loads images folder int memory
        self.explosion_img = pg.image.load(path.join(self.img_folder, 'explosion 577x577.png')).convert_alpha()
        self.player_img = pg.image.load(path.join(self.img_folder, 'blueball 32x32.png')).convert_alpha()
        #load sounds
        self.explosion_sound = pg.mixer.Sound(path.join(self.snd_folder,'explosion.mp3'))
        self.vineboom_sound = pg.mixer.Sound(path.join(self.snd_folder,'vine_boom.mp3'))
        #loads images from images folder when load date is called


    def new(self):
        self.dt = self.clock.tick(FPS) / 10000
        # keep loop running at the right speed
        # the sprite Group allows us to upate and draw sprite in grouped batches
        self.load_data()
        #sprite groups to differentiate between types of sprites
        self.all_sprites = pg.sprite.Group()
        #objects means all sprites that make it harder to keep ball up
        self.all_objects = pg.sprite.Group()
        self.all_colliding_objects = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_balls = pg.sprite.Group()

        #spawning grounds

        #creatde sprites
        #establish when game is craeated
        self.start_time = pg.time.get_ticks()

        #creating a floor with wall sprites along the bottom of the screen
        for floortile in range(TILE_W):
            #generate multiple layer of walls depending on how thick floor should be
            for layer in range(3):
                w = Wall(self, floortile, TILE_H-layer)

        
        #spawn player and ball in the middle of the screen
        self.player = Player(self,0,0)
        self.ball = Ball(self,0,0)
        self.player.rect.center = (WIDTH/2,300)
        self.player.pos = vec(self.player.rect.x,self.player.rect.y)
        self.ball.rect.center = (WIDTH/2,20)
        self.ball.pos = vec(self.ball.rect.x, self.ball.rect.y)

        w = Bouncer(self,True, 150,100 )
        w = Bouncer(self,True, 150,100 )
        w = Bouncer(self,True, 150,100 )
        w = Bouncer(self,True, 150,100 )
        #eb = EvilBall(self)
        t = timebomb(self, 167,89)
        #making walls right outside of screen so player cant walk off the screen into the void
        #2 walls l and r
        for walls in range(TILE_H):
            w = Wall(self,-1,walls)
        for walls in range(TILE_H):
            w = Wall(self,TILE_W, walls)


    def run(self):
        while self.playing == True:
            self.dt = self.clock.tick(FPS) / 10000
            # keep loop running at the right speed
            # input
            self.events()
            # process=-
            self.update()
            # output
            self.draw()
        pg.quit()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                print("the end is near")
                self.playing = False

    def draw_text(self, surface, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        surface.blit(text_surface, text_rect)

    def draw(self):
        #black sreen
        self.screen.fill(BLACK)
        #draw sprites
        self.all_sprites.draw(self.screen)
        self.draw_text(self.screen,str(self.time_display/1000),10,WHITE,25, 5)
        #display text and time when win
        if self.lose:
            self.draw_text(self.screen,"you win", 40, WHITE, WIDTH/2, HEIGHT/2)
            self.draw_text(self.screen,str(self.time_display/1000), 30, WHITE, WIDTH/2, HEIGHT/2+40)
        pg.display.flip()

    def update(self):
    #     if _____:
    #         self.lose = True
    #lose con later

        #stop timer running if win
        #if not self.win and not self.player.dead:
        self.time_display = pg.time.get_ticks()-self.start_time
        self.all_sprites.update()
        # #making a timer
        # self.time = pg.time.get_ticks()//1000
        


if __name__ == "__main__":
    #   create instance of the Game class
    g = Game()
    g.new()
    g.run()