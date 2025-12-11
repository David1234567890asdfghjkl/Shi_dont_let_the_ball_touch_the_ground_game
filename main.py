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
      pg.display.set_caption("Shi_dont_let_the_ball_touch_the_ground_game")
      self.playing = True
      self.running = True
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
        self.defuse_sound = pg.mixer.Sound(path.join(self.snd_folder,'defuse.mp3'))
        self.click_sound = pg.mixer.Sound(path.join(self.snd_folder,'click.mp3'))
        self.ding_sound = pg.mixer.Sound(path.join(self.snd_folder,'ding.mp3'))
        #music
        #posted by DERER1 on youtube
        self.loading_music = path.join(self.snd_folder,'LoadingScreenThemeDERER1.mp3')
        self.theme = path.join(self.snd_folder,'Splashing Around.mp3')
        self.tick_sound = path.join(self.snd_folder,'tick.mp3')
        #loads images from images folder when load date is called


    def new(self):
        #loop music
        pg.mixer.music.load(self.theme)
        pg.mixer.music.play(loops=-1)

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
        #like the mechanics of the game, fun
        #wonder if you could make it so therees a pause menu after death
        #felsh out menus
        
        #spawn player and ball in the middle of the screen
        self.player = Player(self,0,0)
        self.ball = Ball(self,0,0)
        self.player.rect.center = (WIDTH/2,300)
        self.player.pos = vec(self.player.rect.x,self.player.rect.y)
        self.ball.rect.center = (WIDTH/2,20)
        self.ball.pos = vec(self.ball.rect.x, self.ball.rect.y)
        #create spawn manager
        self.spawner = SpawnManager(self)
        #making walls right outside of screen so player cant walk off the screen into the void
        #2 walls l and r
        for walls in range(TILE_H):
            w = Wall(self,-1,walls)
        for walls in range(TILE_H):
            w = Wall(self,TILE_W, walls)
    
    #wait for keys and show start screen from https://github.com/ccozort/cozort__tower_of_the_apprentice/commit/f27da30a4eabff79c09ceddfe41cdcc39321038f#diff-b10564ab7d2c520cdd0243874879fb0a782862c3c902ab535faabe57d5a505e1R140-R142
    def wait_for_key(self):
        #wait for keys and when key pressed, break while loop to continue
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False
    def show_start_screen(self):
        #wait for a key press and then start game
        #game splash/start screen
        pg.mixer.music.load(self.loading_music)
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BLACK)
        self.draw_text(self.screen,"PRESS A KEY TO START", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def run(self):
        while self.playing == True:
            self.dt = self.clock.tick(FPS) / 10000
            # keep loop running at the right speed
            # input
            self.events()
            # process=-
            if not self.lose:
                self.update()
            else:
                #play ding if lose
                pg.mixer.Sound.play(self.ding_sound)
            # output
            self.draw()
        pg.quit()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
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
            self.draw_text(self.screen,"you did let the ball touch the ground", 20, WHITE, WIDTH/2, HEIGHT/2)
            self.draw_text(self.screen,str(self.time_display/1000), 15, WHITE, WIDTH/2, HEIGHT/2+20)
        self.draw_text(self.screen,str(self.spawner.spawn_list[0][3]), 10, WHITE, WIDTH/2, HEIGHT/2+20)
        pg.display.flip()

    def update(self):
        #stop timer running if win
        if not self.lose:
            self.time_display = pg.time.get_ticks()-self.start_time
        self.all_sprites.update()
        self.spawner.spawn()
        # #making a timer
        # self.time = pg.time.get_ticks()//1000
        


if __name__ == "__main__":
    #   create instance of the Game class
    g = Game()
    g.load_data()
    g.show_start_screen()
    while g.running:
        g.new()
        g.run()