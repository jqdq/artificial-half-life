

UPPER_LIMIT = 600
TURN_LIMIT = 10000

ENABLE_PG = False
ENABLE_CSV = 'detail'
IS_NUMERICAL = True
CSV_FP = 'data/data2'
ENABLE_JSON = False
JSON_FP = 'data/json/r'
SAVE_INTERVAL = 9
ATTRIBUTES_TO_SAVE = ['id', 'x', 'y', 'gender', 'source', 'breeding_need', 'energy', 'speed', 'interest_threshold',
                      'interest_eating', 'breeding_threshold', 'mutation_chance']
# Used only when in detail mode


SECTION_AMOUNT = 6
ANIMAL_AMOUNT = 36*3
START_FOOD = 60
PLANT_AMOUNT = 700

GENE_LEN = 10
ANIMAL_ATTRIBS = {'speed': 2,                   # Format - Attribute name : dominating value
                  'interest_threshold': 1,
                  'interest_eating': 1,
                  'breeding_threshold': 5,
                  'mutation_chance': 4}


EATING_LOG = None
SIGHT = 10
LOSE_PER_TURN = 0
DEATH = True
START_BREEDING = -4
REGEN_PER_TURN = 10
PLANT_NUTRITION = 32
