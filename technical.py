
from random import random
import pandas as pd
from json import dump, load
from os import path
from sys import exit

with open('config.json', 'r') as target:
    config = load(target)

def distance(a, b):
    '''Come time ago this was harder'''
    return a-b


def modify_string(val, pos, new_val):
    '''Used to modify genome, basically `val[pos] = new_val` for strings'''
    return ''.join(new_val if i == pos else val[i] for i in range(len(val)))

def modify4cam(value, camera, screen, x_or_y):
    """Calculates values for drawing on screen"""
    return (value - camera[x_or_y]) * 2 ** camera['scale'] + (
        screen.get_size()[{'x': 0, 'y': 1}[x_or_y]] / 2
    )

'''
Genome manipulation
'''


def read_oz(val):
    '''Sums all "1" in the string'''
    assert set(val).issubset({'0', '1'}), f'Niepoprawna notacja: {val}'
    return val.count('1')


def random_oz(dom=config['GENE_LEN']/2, length=config['GENE_LEN']):
    ''' Generates a random string '''
    chance_threshold = dom/length
    return ''.join(
        '1' if random() < chance_threshold else '0' for _ in range(length)
    )


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
            g = [
                cls(
                    s,
                    (i, j),
                    [i * cls.size, (i * cls.size) + cls.size - 1],
                    [j * cls.size, (j * cls.size) + cls.size - 1],
                )
                for j in range(size)
            ]

            s.append(g)
        return s

    def __init__(self, parent, parent_id, min_max_x, min_max_y, elements=[]):
        """A subclass of Set used to improve performance of local searching.

        Arguments:
            parent {list} -- List which will be later used as a map
            parent_id {[int, int]} -- Coordinates of the object in parent
            min_max_x {[int, int]} -- Min and max values of x coordinates of an object in this sector
            min_max_y {[int, int]} -- Min and max values of y coordinates of an object in this sector

        Keyword Arguments:
            elements {list} -- List of elements in this field (default: {[]})
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
        inside = ''.join(str(i)+';' for i in self)
        return f"{self.x[0]}-{self.x[1]};{self.y[0]}-{self.y[1]}: {inside}"

    def add(self, obj):
        """Adds an object to the Section"""

        if not self.not_in_range(obj.x, obj.y):
            super().add(obj)
        else:
            raise Exception("Object not in this sector's range")

    def next(self, *pos):
        """Returns the object on the left/right/up/down (these can be simpy written and it will work
        It also takes 2 ints as arguments which will be used as vectors.
        """
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
        """Check if coordinates are in Section's range"""
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
attr_dict = {"ID": 'id', "x coordinates": 'x', "y coordinates": 'y', "Gender": 'gender', "Parents": 'source', "Breeding need": 'breeding_need', "Energy": 'energy', "Speed gene": 'speed', "Attention threshold gene": 'interest_threshold',
                    "Interest in eating gene": 'interest_eating', "Breeding threshold gene": 'breeding_threshold', "Mutation resistance": 'mutation_res'}


def save_detail(fp, animal_list, turn):
    '''Creates a detailed CSV with data of every animal'''
    try:
        if not path.exists(fp+'.csv'):
            with open(fp+'.csv', 'w', newline='\n') as csvfile:
                csvfile.write(
                    "turn"+";"+";".join(attr_dict[config['ATTRIBUTES_TO_SAVE']])+"\n")
        with open(fp+'.csv', 'a', newline='\n') as csvfile:
            for i in animal_list:
                data = [str(j) for j in i.get_data(
                    attr_dict[config['ATTRIBUTES_TO_SAVE']]).values()]
                csvfile.write(str(turn)+";"+";".join(data)+"\n")
    except FileNotFoundError:
        print("SAVE LOCATION NOT FOUND")
        exit(1)


def save_summary(fp, animal_list, plant_list, turn):
    '''Creates a shorter CSV with a summary of the simulation. Calculates longer.'''
    attributes = ['energy', 'speed', 'interest_threshold',
                  'interest_eating', 'breeding_threshold', 'mutation_res']
    try:
        if not path.exists(fp+'.csv'):
            attr_names = ['turn', 'animal_amount', 'plant_amount']
            for i in attributes:
                attr_names.append(i+'_med')
                attr_names.append(i+'_dev')
            with open(fp+'.csv', 'w', newline='\n') as csvfile:
                csvfile.write(";".join(attr_names)+"\n")
    except FileNotFoundError:
        print("SAVE LOCATION NOT FOUND")
        exit(1)

    # Calculating statistics
    df = pd.DataFrame(columns=attributes, dtype=int)
    for i in animal_list:
        df = df.append(i.get_data(attributes), ignore_index=True)
    if config['IS_NUMERICAL']:
        deviation = df.std().round(decimals=3)
        med = df.mean().round(decimals=3)
    else:
        deviation = (df.quantile(0.75)-df.quantile(0.25))/2
        med = df.quantile(0.5)

    stats = [str(len(animal_list)), str(len(plant_list))]
    for i in attributes:
        stats.append(str(med[i]))
        stats.append(str(deviation[i]))

    # Writing
    try:
        with open(fp+'.csv', 'a', newline='\n') as csvfile:
            text = str(turn)+";"+";".join(stats)+"\n"
            csvfile.write(text)
    except FileNotFoundError:
        print("SAVE LOCATION NOT FOUND")
        exit(1)


def save_json(fp, animal_list, turn):
    '''Creates a JSON with even more detailed information about every animal (one JSON for one turn)'''
    data = {}
    for i in animal_list:
        g = i.get_for_json()
        data[g[0]] = g[1]
    try:
        with open(f"{fp}_{turn}.json", 'w') as file:
            dump(data, file)
    except FileNotFoundError:
        print("SAVE LOCATION NOT FOUND")
        exit(1)