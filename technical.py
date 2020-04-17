
from random import random
import pandas as pd
from json import dump
from os import path
from config import GENE_LEN
from os import path


def distance(a, b):
    return a-b


def modify_string(val, pos, new_val):
    new = ''
    for i in range(len(val)):
        if i == pos:
            new += new_val
        else:
            new += val[i]
    return new


'''
One Zero genes basic manipulation
'''


def read_oz(val):
    assert set(val).issubset({'0', '1'}), f'Niepoprawna notacja: {val}'
    g = 0
    for i in val:
        if i == '1':
            g += 1
    return g


def random_oz(dom=GENE_LEN/2, length=GENE_LEN):
    chance_threshold = dom/GENE_LEN
    val = ''
    for _ in range(length):
        if random()<chance_threshold:
            val += '1'
        else:
            val += '0'
    return val


'''
Map representation
'''


class Section(set):
    size = 40

    @classmethod
    def genmap(cls, size):
        """Generates a square area filled with Section objects.

        Arguments:
            size {int} -- length of the square's side

        Returns:
            list -- 2 level nested list filled with Section instances
        """
        s = []
        for i in range(size):
            g = []
            for j in range(size):
                g.append(cls(s, (i, j), [
                         i*cls.size, (i*cls.size)+cls.size-1], [j*cls.size, (j*cls.size)+cls.size-1]))
            s.append(g)
        return s

    def __init__(self, parent, parent_id, min_max_x, min_max_y, elements=[]):
        """Tworzy sekcję (subklasę zbioru) pozwalając na ograniczenie przeszukiwania planszy.

        Arguments:
            parent {list} -- mapa 
            parent_id {[int, int]} -- położenie obiektu w parent
            min_max_x {[int, int]} -- minimalne i maksymalne koordynaty x przypisania do sektora (przedział zamknięty obustronnie)
            min_max_y {[int, int]} -- minimalne i maksymalne koordynaty y przypisania do sektora (przedział zamknięty obustronnie)

        Keyword Arguments:
            elements {list} -- Lista obiektów istniejących na polu (default: {[]})
        """
        super().__init__(elements)
        assert len(parent_id) == 2, "Niepoprawne id"
        assert len(min_max_x) == 2, "Niepoprawne wartości min i max x"
        assert len(min_max_y) == 2, "Niepoprawne wartości min i max y"
        self.parent = parent
        self.x = min_max_x
        self.y = min_max_y
        self.parent_id = parent_id

    def __str__(self):
        inside = ''
        for i in self:
            inside += str(i)+';'
        return f"{self.x[0]}-{self.x[1]};{self.y[0]}-{self.y[1]}: {inside}"

    def add(self, obj):
        """Dodaje obiekt do sekcji

        Arguments:
            obj {obiekt} -- obiekt do dodania

        Raises:
            Exception: Obiekt nie mieści się w min_max_x lub min_max_y sektora

        Returns:
            None
        """

        if not self.not_in_range(obj.x, obj.y):
            super().add(obj)
        else:
            raise Exception("Obiekt poza zasięgiem sektora")

    def next(self, *pos):
        """Zwraca obiekt z określonej pozycji, lub określonego sąsiada, gdy pos=left/right/up/down"""
        if isinstance(pos, str):
            pos = {'left': [-1, 0], 'right': [1, 0],
                   'up': [0, 1], 'down': [0, -1]}[pos]
        try:
            sec = self.parent[self.parent_id[0] +
                              pos[0]][self.parent_id[1]+pos[1]]
        except IndexError:
            sec = {}
        return sec

    def not_in_range(self, x, y):
        """Sprawdza, czy koordynaty x, y znajdują się w zasięgu sekcji. Jeśli nie zwraca wektor kierunku do poprawnego sektora
        """
        _info = [0, 0]
        if y > self.y[1]:
            _info[1] = 1
        elif self.y[0] > y:
            _info[1] = -1
        if x > self.x[1]:
            _info[0] = 1
        elif self.x[0] > x:
            _info[0] = -1
        if _info == [0, 0]:
            return False
        else:
            return _info


'''
DATA EXTRACTION
'''


def save_detail(fp, attributes, animal_list, turn):
    if not path.exists(fp+'.csv'):
        with open(fp, 'w', newline='\n') as csvfile:
            csvfile.write("turn"+"\t"+"\t".join(attributes)+"\n")
    with open(fp+'.csv', 'a', newline='\n') as csvfile:
        for i in animal_list:
            data = i.get_data(attributes).values()
            csvfile.write(str(turn)+"\t"+"\t".join(data)+"\n")


def save_summary(fp, animal_list, plant_list, turn):
    attributes = ['energy', 'speed', 'interest_threshold',
                  'interest_eating', 'breeding_threshold', 'mutation_chance']
    if not path.exists(fp+'.csv'):
        attr_names = ['turn', 'animal_amount', 'plant_amount']
        for i in attributes:
            attr_names.append(i+'_med')
            attr_names.append(i+'_dev')
        with open(fp+'.csv', 'w', newline='\n') as csvfile:
            csvfile.write(";".join(attr_names)+"\n")

    # Calculating statistics
    df = pd.DataFrame(columns=attributes, dtype=int)
    for i in animal_list:
        df = df.append(i.get_data(attributes), ignore_index=True)
    deviation = (df.quantile(0.75)-df.quantile(0.25))/2
    med = df.quantile(0.5)

    stats = [str(len(animal_list)), str(len(plant_list))]
    for i in attributes:
        stats.append(str(med[i]))
        stats.append(str(deviation[i]))

    # Writing
    with open(fp+'.csv', 'a', newline='\n') as csvfile:
        text = str(turn)+";"+";".join(stats)+"\n"
        csvfile.write(text)


def save_json(fp, animal_list, turn):
    data = dict()
    for i in animal_list:
        g = i.get_for_json()
        data[g[0]] = g[1]
    dump(data, f"{fp}_{turn}.json")
