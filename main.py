import sys
from math import sqrt
from random import choice, random, randrange
from time import sleep

import pygame as pg

from config_GUI import configure
from species import Animal, Life, Plant, config
from technical import Section, distance, save_detail, save_json, save_summary, config, modify4cam

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
        screen = pg.display.set_mode(size=(800,800), flags=pg.RESIZABLE)
        pg.display.set_caption("AL simulation")
        framerate = pg.time.Clock()
        camera = {'x':100,'y':100,'scale':2}
        FPS = 6
        paused = False
    else:
        screen = None
        camera = None

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

        ### PyGame stuff ###
        if config['ENABLE_PG']:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)
                if event.type == pg.VIDEORESIZE:
                    surface = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
            
            # User input handling
            if pg.key.get_pressed()[pg.K_SPACE]: # Pausing
                paused = not paused
                pg.time.wait(250)
            if pg.key.get_pressed()[pg.K_PAGEUP] or pg.key.get_pressed()[pg.K_EQUALS]:
                if camera['scale']<5:
                    camera['scale'] += 1
            if pg.key.get_pressed()[pg.K_PAGEDOWN] or pg.key.get_pressed()[pg.K_MINUS]:
                if camera['scale']>0:
                    camera['scale'] -= 1
            if pg.key.get_pressed()[pg.K_UP]:
                camera['y'] -= 20
            if pg.key.get_pressed()[pg.K_DOWN]:
                camera['y'] += 20
            if pg.key.get_pressed()[pg.K_LEFT]:
                camera['x'] -= 20
            if pg.key.get_pressed()[pg.K_RIGHT]:
                camera['x'] += 20
            
            # Paused game handling
            if paused: 
                pg.display.flip()
                framerate.tick(FPS)
                continue
            screen.fill((0, 0, 0))

        turn += 1

        ### Obsługa roślin ###
        for _ in range(config['REGEN_PER_TURN']):
            plants.append(Plant(plants, Section.size*section_sqrt,
                                Section.size*section_sqrt, search_sectors))

        # Plant drawing
        if config['ENABLE_PG']:
            for d in plants:
                pg.draw.rect(screen, (0, 255, 0), (modify4cam(d.x, camera, screen, 'x'), modify4cam(d.y, camera, screen, 'y'), 2**camera['scale'], 2**camera['scale']), 0)

        ### Obsługa gatunku wybranego ###
        # Animal drawing
        if config['ENABLE_PG']:
            for d in animals:
                if d.breeding_need <= config['START_BREEDING']+4:
                    pg.draw.rect(screen, (0, 0, 255), (modify4cam(d.x, camera, screen, 'x'), modify4cam(d.y, camera, screen, 'y'), 2**camera['scale'], 2**camera['scale']), 0)
                else:
                    pg.draw.rect(screen, (255, 255, 255),
                                 (modify4cam(d.x, camera, screen, 'x'), modify4cam(d.y, camera, screen, 'y'), 2**camera['scale'], 2**camera['scale']), 0)

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
                d.move(d.whereto(target, screen, camera), Section.size*section_sqrt)
            if d.energy <= 0 and config['DEATH']:
                d.die()
            if random() < 0.1**(d.mutation_res/2.5):
                d.mutate()
            d.breeding_need += 1
            d.energy -= config['LOSE_PER_TURN']

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
            if config['ANIMAL_LIMIT']>0 and len(animals) >= config['ANIMAL_LIMIT']:
                break
            print('\n=====================', turn, '::', len(
                animals), '=====================\n')
            animal_counter = len(animals)
        if config['TURN_LIMIT']>0 and turn >= config['TURN_LIMIT']:
            break

        if config['ENABLE_PG']:
            pg.display.flip()
            framerate.tick(FPS)  # Ustawia szybkość w fps

    print('\n'*2, 'Simulation ended', '\a\a\a', '\n'*2)
