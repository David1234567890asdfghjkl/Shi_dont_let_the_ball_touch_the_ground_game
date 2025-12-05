#tilemap
from settings import *
import pygame as pg
import time
import math
vec = pg.math.Vector2
#map object
class Map:
    #filename is the file class calls
    def __init__(self, filename):
        #list to hold map data
        self.data = []
        #getting tilemap data by openning file named filename text file
        with open(filename, 'rt') as f:
            for line in f:
                #remove line breaks in line and add to data
                self.data.append(line.strip())
        
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * 32
        self.height = self.tileheight * 32

#timer class 
    #can be started with start() and will return true or false based on if time is up with ready()
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        self.time = time
        #timertime is how much time passed since start
        self.timertime = 0
    #start timer by making the the start time the current time
    def start(self):
        self.start_time = pg.time.get_ticks()
    #if the self.time has passed since start time, return true
    def ready(self):
        current_time = pg.time.get_ticks()
        self.timertime = current_time - self.start_time
        if current_time - self.start_time >= self.time:
        #True = timer finished
            return True
        return False

def calculatedist(co1,co2):
    return math.sqrt((co1[0]-co2[0])**2+(co1[1]-co2[1])**2)

#this class manages all spawning of enemy psirtes
class SpawnManager():
    def __init__(self):
        #list says all the sprites to spawn
        self.spawn_list = []

def kick(kicker,kicked,kick_scalar):
        #get direction to kick the kicked by getting the difference between coords of player and ball
            #kick ball in direction directly away from kicker
        direction = vec(kicker.rect.center)-vec(kicked.game.ball.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()
        #slope of line pointing to kicked
        #direction vector multiplied by kick force scalar
        kicker.game.ball.vel = direction * -kick_scalar

#linear increase/decrease/nothing for each color value
def gradient(ratior=0, beginr=0, finalr=0, ratiog=0, beging=0, finalg=0, ratiob=0, beginb=0, finalb=0):
    return (ratior*(finalr-beginr)+beginr,beging+ratiog*(finalg-beging),beginb+ratiob*(finalb-beginb))