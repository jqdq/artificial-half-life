import logging
import sys
from math import sqrt
from random import choice, random, randrange
from time import sleep

import pygame as pg

from config_GUI import configure
from species import Animal, Life, Plant, config
from technical import Section, distance, save_detail, save_json, save_summary, config

if __name__ == "__main__":

    # 24 Potem Bóg rzekł: «Niechaj ziemia wyda istoty żywe różnego rodzaju: bydło,
    # zwierzęta pełzające i dzikie zwierzęta według ich rodzajów!» I stało się tak.
    # 25 Bóg uczynił różne rodzaje dzikich zwierząt, bydła i wszelkich zwierząt
    # pełzających po ziemi. I widział Bóg, że były dobre.

    config = configure()
    if config==None:
        sys.exit(0)

    ''' SETUP '''
    ### Generowanie mapy ###

    section_sqrt = config['SECTION_AMOUNT']

    if config['ENABLE_PG']:
        pg.init()
        screen = pg.display.set_mode(size=(
            2*Section.size*section_sqrt, 2*Section.size*section_sqrt), flags=0, depth=0, display=0)
        framerate = pg.time.Clock()
    else:
        screen = None

    search_sectors = Section.genmap(section_sqrt)

    ### Produkcja startowej biosfery ###

    animals = []
    for i in range(config['ANIMAL_AMOUNT']):
        animals.append(Animal(animals, randrange(0, Section.size*section_sqrt),
                              randrange(0, Section.size*section_sqrt), search_sectors, config['START_FOOD'], None, None))

    plants = []
    for i in range(config['PLANT_AMOUNT']):
        plants.append(Plant(plants, Section.size*section_sqrt,
                            Section.size*section_sqrt, search_sectors))

    ''' PRZEBIEG TURY '''
    turn = 0
    animal_counter = len(animals)

    while True:
        turn += 1

        ### PyGame stuff ###
        if config['ENABLE_PG']:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    logging.shutdown()
                    sys.exit(0)
            screen.fill((0, 0, 0))

        ### Obsługa roślin ###
        for _ in range(config['REGEN_PER_TURN']):
            plants.append(Plant(plants, Section.size*section_sqrt,
                                Section.size*section_sqrt, search_sectors))

        if config['ENABLE_PG']:
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
            if d.energy <= 0 and config['DEATH']:
                d.die()
            if random() < 0.1**(d.mutation_res/2.5):
                d.mutate()
            d.breeding_need += 1
            d.energy -= config['LOSE_PER_TURN']
            if config['ENABLE_PG']:
                if d.breeding_need <= config['START_BREEDING']+4:
                    pg.draw.rect(screen, (0, 0, 255), (2*d.x, 2*d.y, 2, 2), 0)
                else:
                    pg.draw.rect(screen, (255, 255, 255),
                                 (2*d.x, 2*d.y, 2, 2), 0)

        ### Data extraction ###

        if turn % (config['SAVE_INTERVAL']+1) == 0:
            if config['ENABLE_JSON']:
                save_json(config['JSON_FP'], animals, turn)
            if config['ENABLE_CSV'] == 2:
                save_detail(config['CSV_FP'], animals, turn)
            elif config['ENABLE_CSV'] == 1:
                save_summary(config['CSV_FP'], animals, plants, turn)

        # Sprawdzanie i zapis ilości zwierząt
        if len(animals) != animal_counter:
            if len(animals) == 0:
                break
            if config['ANIMAL_LIMIT'] and len(animals) >= config['ANIMAL_LIMIT']:
                break
            print('=====================', turn, '::', len(
                animals), '=====================')
            animal_counter = len(animals)
        if config['TURN_LIMIT'] and turn >= config['TURN_LIMIT']:
            break

        if config['ENABLE_PG']:
            pg.display.flip()
            framerate.tick(8)  # Ustawia szybkość w fps

    print('\n'*2, 'Simulation ended', '\a\a\a', '\n'*2)
