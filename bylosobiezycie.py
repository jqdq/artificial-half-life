from random import choice, random, randrange
import logging
from math import sqrt

def distance(a, b):
    if a>b:
        return a-b
    else:
        return b-a

class Section(set):
    size = 20

    @classmethod
    def genmap(cls, size):
        s = []
        for i in range(size):
            g = []
            for j in range(size):
                g.append(cls(s, (i, j), [
                         i*cls.size, (i*cls.size)+cls.size-1], [j*cls.size, (j*cls.size)+cls.size-1]))
            s.append(g)
        return s

    def __init__(self, parent, _id, min_max_x, min_max_y, elements=[]):
        super().__init__(elements)
        assert len(_id) == 2, "Niepoprawne id"
        assert len(min_max_x) == 2, "Niepoprawne wartości min i max x"
        assert len(min_max_y) == 2, "Niepoprawne wartości min i max y"
        self.parent = parent
        self.x = min_max_x
        self.y = min_max_y
        self.id = _id

    def __str__(self):
        inside = ''
        for i in self:
            inside += str(i)+'; '
        return f"{self.x[0]}-{self.x[1]}; {self.y[0]}-{self.y[1]}: {inside}"

    def add(self, obj):
        if not self.not_in_range(obj.x, obj.y):
            super().add(obj)
        else:
            raise Exception("Obiekt poza zasięgiem sektora")

    def next(self, *pos):
        if isinstance(pos, str):
            pos = {'left': [-1, 0], 'right': [1, 0],
                   'up': [0, 1], 'down': [0, -1]}[pos]
        return self.parent[self.id[0]+pos[0]][self.id[1]+pos[1]]

    def not_in_range(self, x, y):
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


class Life(object):

    def __init__(self, x, y, section_list):
        self.x = x
        self.y = y
        self.section = section_list[x//Section.size][y//Section.size]
        self.section.add(self)


class Plant(Life):
    
    def __str__(self):
        return f'Plant [{self.x}, {self.y}]'


class Animal(Life):
    SIGHT_RADIUS = 6

    def __init__(self, x, y, section, speed):
        super().__init__(x, y, section)
        self.speed = speed
        self.energy = 1
        self.breeding_need = -4
        self.interest = 0.1

    def see(self, obj):
        x = distance(self.x, obj.x)
        y = distance(self.y, obj.y)
        dist = sqrt(x**2 + y**2)
        if dist > self.SIGHT_RADIUS:
            return 0
        else:
            return 1/dist

    def __str__(self):
        return f'Animal [{self.x}, {self.y}] speed={self.speed} energy={None}'

    def move(self, direction): #TODO: To nie działa gdy jest zbyt bliżej niż self.speed xD
        assert direction[0]==0 or direction[1]==0, 'Wrong directions'
        self.x = abs(self.x + direction[0])
        self.y = abs(self.y + direction[1])
        shift = self.section.not_in_range(self.x, self.y)
        if shift:
            self.section.remove(self)
            self.section = self.section.next(*shift)
            self.section.add(self)

    def search(self):
        area = self.section.copy()
        peaks = [[self.x-self.SIGHT_RADIUS, self.y-self.SIGHT_RADIUS], [self.x-self.SIGHT_RADIUS, self.y+self.SIGHT_RADIUS],
                 [self.x+self.SIGHT_RADIUS, self.y-self.SIGHT_RADIUS], [self.x+self.SIGHT_RADIUS, self.y+self.SIGHT_RADIUS]]
        for i in peaks:
            if i[0]<0 or i[1]<0:
                continue
            shift = self.section.not_in_range(*i)
            if shift:
                print("Szukanie:", self.section.next(*shift))
                area.update(self.section.next(*shift))
        possible = dict()
        for i in area:
            if i.x == self.x and self.y == i.y:
                continue
            val = self.see(i)
            if val > 0: 
                if isinstance(i, Plant):
                    val /= self.energy/self.speed
                if isinstance(i, Animal) and self.breeding_need>0:
                    val *= self.breeding_need
                if val>self.interest:
                    possible[i] = val
        if len(possible)>0:
            return sorted(possible.items(), key=lambda t: t[1])[-1][0]
        else:
            return None

    def whereto(self, obj):
        a = distance(self.x, obj.x) 
        b = distance(self.y, obj.y)
        if abs(a)>self.speed:
            a = self.speed*a//abs(a)
        if abs(b)>self.speed:
            b = self.speed*b//abs(b)
        if a>b:
            return (a,0)
        elif a==b:
            return choice((a,0), (0,b))
        else:
            return (0,b)

if __name__ == "__main__":
    s = Section.genmap(5)
    d = Animal(15, 5, s, 2)
    f = Plant(16, 5, s)
    g = Plant(21, 5, s)
    # for j in s:
    #     for i in j:
    #         print(i)
    a = d.search()
    print(a)
    d.move(d.whereto(a))
    print(d)
    a = d.search()
    print(a)
    d.move(d.whereto(a))
    print(d)
    # d.move('right')

    # print(1*'\n')
    # print(d.search())
    # d.move('up')

    # print(1*'\n')
    # print(d.search())
