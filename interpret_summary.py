'''
DISCLAIMER

The script is meant do be use to create a simple visualization of CSV from summary mode

'''
import pandas as pd
import matplotlib.pyplot as plt

FP = 'data/data1.csv'
ATTRIB = ['speed', 'interest_threshold',
          'interest_eating', 'breeding_threshold', 'mutation_res']

df = pd.read_csv(FP, delimiter=';', index_col='turn')

plt.figure(0)
plt.subplot(2, 1, 1)
plt.title("Populacja", fontsize=11)
plt.plot(df['animal_amount'], label="Liczba zwierząt")
plt.plot(df['plant_amount'], label='Liczba roślin')
#plt.ylim(0, 1000)
plt.xticks(df.index[::20], rotation=70, fontsize=7.5,
           ha='right', rotation_mode="anchor")
plt.xlabel('Tura', fontsize=9)
plt.grid()

plt.subplot(2, 1, 2)
plt.title("Energia w populacji zwierząt")
plt.errorbar(df.index, df['energy_med'],
             yerr=df['energy_dev'], errorevery=10, elinewidth=0.5)
plt.xticks(df.index[::20], rotation=70, fontsize=7.5,
           ha='right', rotation_mode="anchor")
plt.xlabel('Tura', fontsize=9)
plt.grid()
plt.tight_layout()
plt.savefig('0', dpi=100)

for i in range(len(ATTRIB)):
    plt.figure((i//2)+1)
    plt.subplot(2, 1, (i % 2)+1)
    plt.title(f"Gen {ATTRIB[i]} w populacji zwierząt")
    plt.errorbar(df.index, df[ATTRIB[i]+'_med'],
                 yerr=df[ATTRIB[i]+'_dev'], errorevery=5, elinewidth=0.5)
    plt.yticks(ticks=[i for i in range(1, 11)])
    plt.ylabel('Wartość cechy', fontsize=9)
    plt.xticks(df.index[::20], rotation=70, fontsize=7.5,
               ha='right', rotation_mode="anchor")
    plt.xlabel('Tura', fontsize=9)
    plt.grid()
    if i % 2 == 1:
        plt.tight_layout()
        plt.savefig(str(i+1), dpi=100)

if len(ATTRIB) % 2 == 1:
    plt.savefig(str(len(ATTRIB)), dpi=100)

# plt.show()
