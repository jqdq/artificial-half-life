import logging
import sys
from math import sqrt
from random import choice, random, randrange
from time import sleep

import pygame as pg

from config import ANIMAL_AMOUNT, PLANT_AMOUNT, SECTION_AMOUNT, START_FOOD, START_BREEDING, REGEN_PER_TURN, LOSE_PER_TURN
from species import Animal, Life, Plant
from technical import Section, distance

if __name__ == "__main__":

    # 24 Potem Bóg rzekł: «Niechaj ziemia wyda istoty żywe różnego rodzaju: bydło,
    # zwierzęta pełzające i dzikie zwierzęta według ich rodzajów!» I stało się tak.
    # 25 Bóg uczynił różne rodzaje dzikich zwierząt, bydła i wszelkich zwierząt
    # pełzających po ziemi. I widział Bóg, że były dobre.

    ''' SETUP '''
    ### Generowanie mapy ###

    section_sqrt = int(sqrt(SECTION_AMOUNT))

    pg.init()
    screen = pg.display.set_mode(size=(
        2*Section.size*section_sqrt, 2*Section.size*section_sqrt), flags=0, depth=0, display=0)
    framerate = pg.time.Clock()

    search_sectors = Section.genmap(section_sqrt)

    ### Produkcja startowej biosfery ###

    animals = []
    for i in range(ANIMAL_AMOUNT):
        animals.append(Animal(animals, randrange(0, Section.size*section_sqrt),
                              randrange(0, Section.size*section_sqrt), search_sectors, START_FOOD))

    plants = []
    for i in range(PLANT_AMOUNT):
        plants.append(Plant(plants, randrange(0, Section.size*section_sqrt),
                            randrange(0, Section.size*section_sqrt), search_sectors))

    ''' PRZEBIEG TURY '''

    while True:
        ### PyGame stuff ###
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                logging.shutdown()
                sys.exit(0)
        screen.fill((0, 0, 0))

        ### Obsługa roślin ###
        for _ in range(REGEN_PER_TURN):
            plants.append(Plant(plants, randrange(0, Section.size*section_sqrt),
                                randrange(0, Section.size*section_sqrt), search_sectors))

        for d in plants:
            pg.draw.rect(screen, (0, 255, 0), (2*d.x, 2*d.y, 2, 2), 0)

        ### Obsługa gatunku wybranego ###

        for d in animals[:]:
            target = d.search()
            if target == None:
                d.move(d.random_walk(), Section.size*section_sqrt)
            elif target.x == d.x and target.y == d.y:
                if isinstance(target, Plant):
                    d.eat(target)
                if isinstance(target, Animal) and d.breeding_need >= d.breeding_threshold and target.breeding_need >= target.breeding_threshold:
                    d.breed(target)
            else:
                d.move(d.whereto(target, screen), Section.size*section_sqrt)
            if d.energy <= 0:
                d.die()
            if random() < 0.1**(d.mutation_chance/2):
                d.mutate()
            d.breeding_need += 1
            d.energy -= LOSE_PER_TURN
            if d.breeding_need <= START_BREEDING+4:
                pg.draw.rect(screen, (0, 0, 255), (2*d.x, 2*d.y, 2, 2), 0)
            else:
                pg.draw.rect(screen, (255, 255, 255), (2*d.x, 2*d.y, 2, 2), 0)

        print('=====================', len(animals) , '=====================')
        pg.display.flip()
        framerate.tick(8)  # Ustawia szybkość w fps
