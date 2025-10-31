#tilemap
from settings import *
import pygame as pg
import time
import math
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
    #start timer by making the the start time the current time
    def start(self):
        self.start_time = pg.time.get_ticks()
    #if the self.time has passed since start time, return true
    def ready(self):
        current_time = pg.time.get_ticks()
        if current_time - self.start_time >= self.time:
        #True = timer finished
            return True
        return False

# function to easily set the center of soemthing to a certain tuple 
# parameters are the Surface rect and desired center
def edit_center(rect, desired_center):
    return (desired_center[0] - rect.width/2, desired_center[1] - rect.height/2)

def calculatedist(co1,co2):
    return sqrt((co1[0]-co2[0])^2+(co1[1]-co2[1])^2)