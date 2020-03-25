from random import choice, random, randrange
import logging
from math import sqrt

class Life(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Plant(Life):
    pass

class Animal(Life): 
    SIGHT_RADIUS = 4  

    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.speed = speed

    def __contains__(self, obj):
        x = self.x-obj.x
        y = self.y-obj.y
        return sqrt(x**2 + y**2)<=self.SIGHT_RADIUS

    def pray(self, pray_list):
        """Returns the first object found in range
        
        Arguments:
            pray_list {list} -- List of all prayed on species
        
        Returns:
            Life/None -- Instance of a subclass of Life or None if nothing was found
        """        
        for i in pray_list:
            if i in self:
                return i
        return None

    def move(self, direction):
        assert direction in ['left', 'right', 'up', 'down'], 'Wrong direction'
        if direction in ['up', 'down']:
            a = 0
            b = self.speed
        if direction in ['left', 'right']:
            a = self.speed
            b = 0
        if direction in ['left', 'down']:
            a *= -1
            b *= -1
        self.x += a
        self.y += b

    def whereto(self, obj):
        vector = [self.x-obj.x, self.y-obj.y]
        prop = [['left','right'], ['up','down']]
        for i in [0,1]:
            if vector[i]>0:
                prop[i] = prop[i][0]
            else:
                prop[i] = prop[i][1]
        if abs(vector[0])>abs(vector[1]):
            return prop[0]
        else:
            return prop[1]

    def decide_action(self):
        raise NotImplementedError