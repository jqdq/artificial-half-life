''' BASIC '''
SECTION_AMOUNT = 8**2

UPPER_LIMIT = 500
TURN_LIMIT = 10000

ENABLE_PG = False
ENABLE_CSV = 'summary'  # False, "detail" or "summary"
CSV_FP = 'data/data2'
ENABLE_JSON = False
JSON_FP = 'data/record'
SAVE_INTERVAL = 9
ATTRIBUTES_TO_SAVE = ['energy', 'speed', 'interest_threshold',
                      'interest_eating', 'breeding_threshold', 'mutation_chance']
# Used only when in detail mode
#['id', 'x', 'y', 'energy', 'speed', 'source', 'interest_threshold',
# 'interest_eating', 'breeding_threshold', 'mutation_chance']

''' ANIMAL FEATURES '''
ANIMAL_AMOUNT = 40
START_FOOD = 30

CONSUMPTION = True
EATING_LOG = 12
SIGHT = 10
LOSE_PER_TURN = 0
DEATH = True

GENE_LEN = 10
START_BREEDING = -4
ANIMAL_ATTRIBS = {'speed':2,                   # Format - Attribute name : dominating value 
                  'interest_threshold':5,
                  'interest_eating':5, 
                  'breeding_threshold':5, 
                  'mutation_chance':2}

''' PLANTS '''
PLANT_AMOUNT = 200
REGEN_PER_TURN = 8

PLANT_NUTRITION = 35
