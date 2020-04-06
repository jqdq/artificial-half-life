import logging
from math import sqrt
from random import choice, random, randrange

import pygame.draw

from config import CONSUMPTION
from technical import Section, distance, read_oz, random_oz


class Life(object):

    def __init__(self, parent, x, y, section_list):
        """Tworzy obiekt żyjący
        
        Arguments:
            parent {iterable} -- zbiór organizmów gatunku
            x {int} -- koordynaty
            y {int} -- koordynaty
            section_list {[[Section,...],...]} -- "Mapa" używana do szukania celu przez zwierzęta
        """        
        self.x = x
        self.y = y
        self.parent = parent
        self.section = section_list[x//Section.size][y//Section.size]
        self.section.add(self)

    def die(self):
        ''' Zabija organizm usuwając wszystkie jego wzmianki'''
        self.section.discard(self)
        self.parent.remove(self)


class Plant(Life):
    nutrition = 10

    def __str__(self):
        return f'Plant [{self.x}, {self.y}]'


class Animal(Life):
    sight_radius = None
    attributes = ['speed', 'interest_threshold', 'interest_eating', 'interest_breeding', 'mutation_chance']

    @classmethod
    def gencode(cls):
        genes = dict()
        for i in cls.attributes:
            genes[i] = random_oz()
        return genes

    def __init__(self, parent, x, y, section, **genome):
        """Tworzy zwierzę
        
        Arguments:
            parent {iterable} -- zbiór organizmów gatunku
            x {int} -- koordynaty
            y {int} -- koordynaty
            section {[[Section,...],...]} -- "Mapa" używana do szukania celu przez zwierzęta
            speed {int} -- szybkość poruszania się zwierzęcia
        """
        super().__init__(parent, x, y, section)
        self.gender = choice([1, -1])
        self.energy = 50
        self.breeding_need = -4
        if genome==dict():
            self.genome = self.gencode()
        else:
            self.genome = genome
        self.interpret()
        logging.info(f"Born {self}")

    def see(self, obj):
        ''' Zwraca ocenę odległości dla obiektu, 0 jeśli poza wzrokiem, 2 jeśli na tym samym polu'''
        x = distance(self.x, obj.x)
        y = distance(self.y, obj.y)
        dist = sqrt(x**2 + y**2)
        if self.sight_radius != None and dist > self.sight_radius:
            return 0
        elif dist == 0:
            return 2
        else:
            return 1/dist

    def __str__(self):
        return f'Animal [{self.x}, {self.y}] speed={self.speed} energy={None}'

    def move(self, direction, map_end, consume=CONSUMPTION):
        """Porusza obiekt zgodnie z wektorem [x,y]
        
        Arguments:
            direction {[int,int]} -- wspomniany wektor
            map_end {[int,int]} -- Pierwsze koordynaty x i y poza mapą
        """        
        assert direction[0] + direction[1] <= self.speed, 'Wrong directions'
        a = abs(self.x + direction[0])
        b = abs(self.y + direction[1])
        if a >= map_end:
            a -= a-map_end+1
        if b >= map_end:
            b -= b-map_end+1
        self.x = a
        self.y = b
        shift = self.section.not_in_range(self.x, self.y)
        if shift:
            self.section.remove(self)
            self.section = self.section.next(*shift)
            self.section.add(self)
        if consume:
            self.energy -= abs(direction[0])+abs(direction[1])

    def search(self):
        ''' Przeszukuje sekcje w polu wzrokowym zwracając najlepszy możliwy cel '''
        area = self.section.copy()
        if self.sight_radius == None or self.sight_radius > Section.size:
            for i in self.section.parent:
                for j in i:
                    area.update(j)
        else:
            peaks = [[self.x-self.sight_radius, self.y-self.sight_radius], [self.x-self.sight_radius, self.y+self.sight_radius],
                     [self.x+self.sight_radius, self.y-self.sight_radius], [self.x+self.sight_radius, self.y+self.sight_radius]]
            for i in peaks:
                if i[0] < 0 or i[1] < 0:
                    continue
                shift = self.section.not_in_range(*i)
                if shift:
                    new = self.section.next(*shift)
                    logging.debug("Szukanie: "+str(new))
                    area.update(new)
        possible = dict()
        for i in area:
            if i == self:
                continue
            val = self.see(i)
            if val > 0:
                if isinstance(i, Plant):
                    val /= self.energy
                elif isinstance(i, Animal):
                    val *= self.breeding_need
                if val > 0.1**self.interest_threshold:
                    possible[i] = val
        if len(possible) > 0:
            return sorted(possible.items(), key=lambda t: t[1])[-1][0]
        else:
            return None

    def whereto(self, obj, screen):
        """Określa koordynaty do poruszania się w kierunku obiektu
        Also maluje na ekranie czerwoną kropkę na celu
        
        Arguments:
            obj {Life} -- obiekt docelowy
            screen {pygame.Display or sth} -- ekran do malowania czerwonej kropy
        
        Returns:
            [int, int] -- wektor poruszania się
        """        
        if screen:
            pygame.draw.rect(screen, (255, 0, 0), (2*obj.x, 2*obj.y, 2, 2), 0)
        a = distance(obj.x, self.x)
        b = distance(obj.y, self.y)
        if abs(a) > self.speed:
            a = self.speed*a//abs(a)
        if abs(b) > self.speed:
            b = self.speed*b//abs(b)
        while abs(a)+abs(b) > self.speed:
            a = a // 2
            b = b // 2
        return a, b

    def random_walk(self):
        """ Generuje randomowy chód """
        a = randrange(-self.speed, self.speed+1)
        b = randrange(-self.speed+abs(a), self.speed+1-abs(a))
        return a, b

    def eat(self, obj):
        """ metoda do jedzenia obj """
        self.energy += obj.nutrition
        logging.debug(f'Eating at [{obj.x}, {obj.y}]')
        obj.die()

    def interpret(self):
        for i in self.genome.items():
            self.__setattr__(i[0],read_oz(i[1]))

    def mutate(self):
        chromosome = choice(self.attributes)
        place = randrange(len(self.genome[chromosome]))
        self.genome[chromosome][place] = {'0':'1','1':'0'}[self.genome[chromosome][place]]
        logging.info(f'Mutacja u {self}. Chromosom {chromosome}: {self.genome[chromosome]}')
