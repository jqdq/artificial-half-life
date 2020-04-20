from math import log, sqrt
from random import choice, random, randrange
import json

import pygame.draw

from technical import Section, distance, modify_string, random_oz, read_oz, modify4cam

with open('config.json', 'r') as target:
    config = json.load(target)


class Life(object):

    def __init__(self, parent, x, y, region):
        """Creates a living object

        Arguments:
            parent {iterable} -- list of all living objects of this type
            x {int} -- spawn coordinate
            y {int} -- spawn coordinate
            region {[[Section,...],...] or Section} -- List of all Section objects or the chosen object
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
        '''Kills the organism'''
        self.section.discard(self)
        self.parent.remove(self)


class Plant(Life):
    nutrition = config['PLANT_NUTRITION']

    def __init__(self, parent, max_x, max_y, region):
        """A plant fot animals to eat
        
        Arguments:
            parent {[Plant objects]} -- List containing all of the plant objects
            max_x {int} -- Highest possible x
            max_y {int} -- Highest possible y
            region {[[Section, ...], ...]} -- List of all Section objects
        """        
        while True:
            x = randrange(0, max_x)
            y = randrange(0, max_y)
            section = region[x//Section.size][y//Section.size]
            end_test = True
            for i in section:
                if i.x == x and i.y == y:
                    end_test = False
                    break
            if end_test:
                break
        super().__init__(parent, x, y, section)

    def __str__(self):
        return f'Plant [{self.x}, {self.y}]'


class Animal(Life):
    sight_radius = config['SIGHT']
    attributes = list(config['ANIMAL_ATTRIBS'].keys())

    @classmethod
    def gencode(cls):
        genes = dict()
        for i in cls.attributes:
            genes[i] = random_oz(dom=config['ANIMAL_ATTRIBS'][i])
        return genes

    ### BUILT-IN ###

    def __init__(self, parent, x, y, section, energy, genome_source, genome):
        """Main object in the symulation - eats, breeds and mutates
        
        Arguments:
            parent {Animal list} -- List containing all of the Animal objects
            x {int} -- spawn coordinates
            y {int} -- spawn coordinates
            section {[[Section,...],...] or Section} -- List of all Section objects or the chosen object
            energy {int} -- starting energy of the animal
            genome_source {[Animal, Animal] or None} -- Parent list
            genome {{attributes:strings consisting of 1 and 0} or None} -- used to calculate corresponding attributes
        """        
        super().__init__(parent, x, y, section)
        self.source = genome_source
        self.gender = choice([1, -1])
        self.energy = energy
        self.breeding_need = config['START_BREEDING']
        self.id = hash(self)
        if not genome:
            self.genome = self.gencode()
        else:
            self.genome = genome
        self.interpret()

    def __str__(self):
        return f'[{self.id} | {self.x}, {self.y}]'

    def __repr__(self):
        return str(self)

    ### OBJECT DETECTION AND MOVEMENT ###

    # Moving

    def whereto(self, obj, screen=None, camera=None):
        """Generates movement vector for the animal
        Creates a red dot on screen if screen and camera are provided

        Arguments:
            obj {Life} -- movement's target
            screen {pygame.Display} -- screen on which red dot will be drawn
            camera {dict} -- defined in main.py

        Returns:
            [int, int] -- the vector
        """
        if screen and camera:
            pygame.draw.rect(screen, (255, 0, 0), (modify4cam(obj.x, camera, screen, 'x'), modify4cam(
                obj.y, camera, screen, 'y'), 2**camera['scale'], 2**camera['scale']), 0)
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
        """ Generates a random movement """
        a = randrange(-self.speed, self.speed+1)
        b = randrange(-self.speed+abs(a), self.speed+1-abs(a))
        return a, b

    def move(self, direction, map_end):
        """Moves the animal according to the provided direction, handles Section change and energy loss

        Arguments:
            direction {[int,int]} -- the movement vector
            map_end {[int,int]} -- first coordinates outside of both bounds
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
        eaten = abs(direction[0])+abs(direction[1])
        if not config['EATING_LOG'] in [0,1]:
            self.energy -= round(eaten * log(eaten, config['EATING_LOG']))
        elif config['EATING_LOG']==0:
            pass
        else:
            self.energy -= eaten

    # Object detection

    def see(self, obj):
        '''Calculates object weight'''
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
        '''Handles target search, returns the best target or None'''
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
                if val > 0.1**self.interest_threshold-config['GENE_LEN']/2:
                    possible[i] = val
        if len(possible) > 0:
            chosen = sorted(possible.items(), key=lambda t: t[1])[-1][0]
            return chosen
        else:
            return None

    ### WORLD INTERACTIONS ###

    def eat(self, obj):
        """ Used to eat other objects """
        self.energy += obj.nutrition
        obj.die()

    def breed(self, partner):
        '''Creates a pretty little Animal from self and partner'''
        # Assertions
        assert self.x == partner.x and self.y == partner.y, "Wrong position"
        assert self.gender != partner.gender, "Same gender"
        # Genome and starting energy calculation
        genome = dict()
        for i in self.attributes:
            cut = randrange(config['GENE_LEN'])
            left = self.genome[i][:cut]
            right = partner.genome[i][cut:]
            genome[i] = left+right
        start_en = self.energy/3 + partner.energy/3
        # Birth
        child = Animal(self.parent, self.x, self.y, self.section,
                       int(start_en), [self.id, partner.id], genome)
        self.parent.append(child)
        print(f"Breeding: {self} and {partner} -> {child}")
        # Libido and energy reduction
        self.energy = int(self.energy*2/3)
        partner.energy = int(partner.energy*2/3)
        self.breeding_need = config['START_BREEDING']
        partner.breeding_need = config['START_BREEDING']

    def die(self):
        super().die()
        print("Death:", self)

    ### GENETICS ###

    def interpret(self, chromosome=None):
        '''Interprets the raw genome'''
        if chromosome:
            val = read_oz(self.genome[chromosome])
            if chromosome == 'speed':
                val += 1
            self.__setattr__(chromosome, val)
        else:
            for i in self.genome.items():
                val = read_oz(i[1])
                if i[0] == 'speed':
                    val += 1
                self.__setattr__(i[0], val)

    def mutate(self):
        '''Creates a mutation in the animal and re-interprets its genome'''
        chromosome = choice(self.attributes)
        old = self.genome[chromosome]
        if random() < 0.5:
            place = randrange(len(self.genome[chromosome]))
            self.genome[chromosome] = modify_string(self.genome[chromosome], place, {
                                                    '0': '1', '1': '0'}[self.genome[chromosome][place]])
        else:
            self.genome[chromosome] = self.genome[chromosome][::-1]
        print(f'Mutation: {self}; {chromosome}: {old} -> {self.genome[chromosome]}')
        self.interpret(chromosome)

    # DATA OUTPUT

    def get_for_json(self):
        ''' Returns Animal's ID and dict with information to export '''
        interpreted = {i: self.__getattribute__(i) for i in self.attributes}
        genome = self.genome
        data = {'parents': self.source, 'position': [self.x, self.y], 'gender': self.gender,
                'breeding_need': self.breeding_need, 'energy': self.energy,
                'interpreted': interpreted, 'genome': genome}
        return self.id, data

    def get_data(self, attrib):
        ''' Returns a dict with specified attributes of the Animal '''
        return {i: self.__getattribute__(i) for i in attrib}
