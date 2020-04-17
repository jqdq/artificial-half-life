''' BASIC '''
SECTION_AMOUNT = 6**2

UPPER_LIMIT = 600
TURN_LIMIT = 10000

ENABLE_PG = False
ENABLE_CSV = 'summary'          # False, "detail" or "summary"
IS_NUMERICAL = True            # if True calculates mean and std instead of the median and quarter deviation
CSV_FP = 'data/data3'
ENABLE_JSON = False
JSON_FP = 'data/record'
SAVE_INTERVAL = 9
ATTRIBUTES_TO_SAVE = ['energy', 'speed', 'interest_threshold',
                      'interest_eating', 'breeding_threshold', 'mutation_chance']
# Used only when in detail mode
# ['id', 'x', 'y', 'energy', 'speed', 'source', 'interest_threshold',
# 'interest_eating', 'breeding_threshold', 'mutation_chance']

''' ANIMAL FEATURES '''
ANIMAL_AMOUNT = 36*3
START_FOOD = 60

CONSUMPTION = True
EATING_LOG = None
SIGHT = 10
LOSE_PER_TURN = 0
DEATH = True

GENE_LEN = 10
START_BREEDING = -4
ANIMAL_ATTRIBS = {'speed': 2,                   # Format - Attribute name : dominating value
                  'interest_threshold': 1,
                  'interest_eating': 1,
                  'breeding_threshold': 5,
                  'mutation_chance': 4}

''' PLANTS '''
PLANT_AMOUNT = 700
REGEN_PER_TURN = 10

PLANT_NUTRITION = 32
