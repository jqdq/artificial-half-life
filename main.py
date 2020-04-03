import logging
from math import sqrt
import sys
from random import choice, random, randrange
from time import sleep

import pygame as pg
from technical import Section, distance
from species import Life, Plant, Animal

''' CONFIG '''
SECTION_AMOUNT = 25
PLANT_AMOUNT = 600
ANIMAL_AMOUNT = 25


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
                              randrange(0, Section.size*section_sqrt), search_sectors, 5))

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

        for d in plants:
            pg.draw.rect(screen, (0, 255, 0), (2*d.x, 2*d.y, 2, 2), 0)

        ### Obsługa gatunku wybranego ###

        for d in animals:
            target = d.search()
            if target == None:
                d.move(d.random_walk(), Section.size*section_sqrt)
            elif target.x == d.x and target.y == d.y:
                if isinstance(target, Plant):
                    d.eat(target)
            else:
                d.move(d.whereto(target, screen), Section.size*section_sqrt)
            pg.draw.rect(screen, (255, 255, 255), (2*d.x, 2*d.y, 2, 2), 0)

        pg.display.flip()
        framerate.tick(4) # Ustawia szybkość w fps