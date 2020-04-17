import logging
from math import log, sqrt
from random import choice, random, randrange

import pygame.draw

from config import (CONSUMPTION, EATING_LOG, GENE_LEN, PLANT_NUTRITION, SIGHT,
                    START_BREEDING, ANIMAL_ATTRIBS)
from technical import Section, distance, modify_string, random_oz, read_oz


class Life(object):

    def __init__(self, parent, x, y, region):
        """Tworzy obiekt żyjący

        Arguments:
            parent {iterable} -- zbiór organizmów gatunku
            x {int} -- koordynaty
            y {int} -- koordynaty
            region {[[Section,...],...] or Section} -- "Mapa" używana do szukania celu przez zwierzęta, albo bezpośrednio sekcja
        """
        self.x = x
        self.y = y
        self.parent = parent
        if isinstance(region, Section):
            self.section = region
        else:
            self.section = region[x//Section.size][y//Section.size]
        self.section.add(self)

    def die(self):
        ''' Zabija organizm usuwając wszystkie jego wzmianki'''
        self.section.discard(self)
        self.parent.remove(self)


class Plant(Life):
    nutrition = PLANT_NUTRITION

    def __init__(self, parent, max_x, max_y, region):
        while True:
            x = randrange(0, max_x)
            y = randrange(0, max_y)
            section = region[x//Section.size][y//Section.size]
            end_test = True
            for i in section:
                if i.x==x and i.y==y:
                    end_test = False
                    break
            if end_test:
                break
        super().__init__(parent, x, y, section)
                    
    def __str__(self):
        return f'Plant [{self.x}, {self.y}]'


class Animal(Life):
    sight_radius = SIGHT
    attributes = list(ANIMAL_ATTRIBS.keys())

    @classmethod
    def gencode(cls):
        genes = dict()
        for i in cls.attributes:
            genes[i] = random_oz(dom=ANIMAL_ATTRIBS[i])
        return genes

    ### BUILT-IN ###

    def __init__(self, parent, x, y, section, energy, genome_source, genome):
        """[summary]

        Arguments:
            parent {[type]} -- [description]
            x {[type]} -- [description]
            y {[type]} -- [description]
            section {[type]} -- [description]
            energy {[type]} -- [description]
            genome_source {[type]} -- [description]
        """
        super().__init__(parent, x, y, section)
        self.source = genome_source
        self.gender = choice([1, -1])
        self.energy = energy
        self.breeding_need = START_BREEDING
        self.breeding_ready = False
        self.id = hash(self)
        if not genome:
            self.genome = self.gencode()
        else:
            self.genome = genome
        self.interpret()

    def __str__(self):
        return f'Animal [{self.id} | {self.x}, {self.y}] speed={self.speed} energy={self.energy}'

    def __repr__(self):
        return str(self)

    ### OBJECT DETECTION AND MOVING ###

    # Moving

    def whereto(self, obj, screen=None):
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
            if abs(a)+abs(b) == 2:
                break
        return a, b

    def random_walk(self):
        """ Generuje randomowy chód """
        a = randrange(-self.speed, self.speed+1)
        b = randrange(-self.speed+abs(a), self.speed+1-abs(a))
        return a, b

    def move(self, direction, map_end, consume=CONSUMPTION):
        """Porusza obiekt zgodnie z wektorem [x,y]

        Arguments:
            direction {[int,int]} -- wspomniany wektor
            map_end {[int,int]} -- Pierwsze koordynaty x i y poza mapą
        """
        assert direction[0] + direction[1] <= self.speed, 'Wrong directions'
        # Obliczanie końcowych koordynatów
        a = abs(self.x + direction[0])
        b = abs(self.y + direction[1])
        # Handling końca mapy
        if a >= map_end:
            a -= a-map_end+1
        if b >= map_end:
            b -= b-map_end+1
        # Przemieszczenie
        self.x = a
        self.y = b
        shift = self.section.not_in_range(self.x, self.y)
        if shift:
            self.section.remove(self)
            self.section = self.section.next(*shift)
            self.section.add(self)
        # Konsumpcja
        if consume:
            eaten = abs(direction[0])+abs(direction[1])
            if EATING_LOG and eaten != 0:
                self.energy -= round(eaten * log(eaten, EATING_LOG))
            else:
                self.energy -= eaten

    # Object detection

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
            if self.see(i) > 0:
                val = self.see(i)
                if isinstance(i, Plant):
                    val /= (0.001+self.energy)/(1+self.interest_eating)
                if isinstance(i, Animal):
                    if i.gender == self.gender:
                        continue
                    else:
                        val *= (self.breeding_need-self.breeding_threshold) * \
                            self.energy/(1+self.speed)
                if val > 0.1**self.interest_threshold-GENE_LEN/2:
                    possible[i] = val
        if len(possible) > 0:
            return choice(sorted(possible.items(), key=lambda t: t[1])[(len(possible)//2):])[0]
        else:
            return None

    ### WORLD INTERACTIONS ###

    def eat(self, obj):
        """ metoda do jedzenia obj """
        self.energy += obj.nutrition
        logging.debug(f'Eating at [{obj.x}, {obj.y}]')
        obj.die()

    def breed(self, partner):
        # Testy, żeby przypału nie było
        assert self.x == partner.x and self.y == partner.y, "Zła pozycja"
        assert self.gender != partner.gender, "Ta sama płeć"
        # Generowanie genomu i startowego najedzenia
        genome = dict()
        for i in self.attributes:
            cut = randrange(GENE_LEN)
            left = self.genome[i][:cut]
            right = partner.genome[i][cut:]
            genome[i] = left+right
        start_en = self.energy/3 + partner.energy/3
        # Narodziny
        child = Animal(self.parent, self.x, self.y, self.section,
                       int(start_en), [self.id, partner.id], genome)
        self.parent.append(child)
        print(f"{child} narodzony z {partner} oraz {self}")
        # Obniżanie libido i energi
        self.energy = int(self.energy*2/3)
        partner.energy = int(partner.energy*2/3)
        self.breeding_need = START_BREEDING
        partner.breeding_need = START_BREEDING

    def die(self):
        super().die()
        print(self, "died")

    ### GENETICS ###

    def interpret(self):
        for i in self.genome.items():
            val = read_oz(i[1])
            if i[0] in ['speed']:
                val += 1
            self.__setattr__(i[0], val)

    def mutate(self):
        chromosome = choice(self.attributes)
        if random() < 0.5:
            place = randrange(len(self.genome[chromosome]))
            self.genome[chromosome] = modify_string(self.genome[chromosome], place, {
                                                    '0': '1', '1': '0'}[self.genome[chromosome][place]])
        else:
            self.genome[chromosome] = self.genome[chromosome][::-1]
        print(
            f'Mutacja u {self}. Chromosom {chromosome}: {self.genome[chromosome]}')
        self.interpret()

    # DATA OUTPUT

    def get_for_json(self):
        interpreted = {i: self.__getattribute__(i) for i in self.attributes}
        genome = self.genome
        data = {'parents': self.source, 'position': [
            self.x, self.y], 'interpreted': interpreted, 'genome': genome}
        return self.id, data

    def get_data(self, attrib):
        return {i: self.__getattribute__(i) for i in attrib}
