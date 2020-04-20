# projekt-si

Just an Artificial Life app with visualization and GUI. You can output data in CSV and JSON formats.

## PyGame preview

In PyGame preview you can move using arrows on your keyboard. Zooming is possible with +/Page up and -/Page down.

## Configuration options

Start conditions:

    - Animal/Plant starting amount - just the amount of the animals/plants you want to start with
    - Starting energy level - the amount of energy provided to every Animal on the start
    - Starting breeding level - Starting animal libido. It resets to this level every time an animal takes part in breeding and rises with every turn. While negative animal will not be able to breed.

Finish conditions - simulation will end if these are reached. Change to 0 to turn them off.

Simulation settings:

    - Map side length - area of the simulation is a square consisting of smaller sections. Each of them has the length of 20. Here you can decide how much of them do you want on one side. The whole map will have the surface of `400n^2`.
    -  Moving modificator - it is possible to change the amount of energy consumed by moving. It's calculated from: `nlog_g(n)`, where `n` is the original cost and g is the value of this option. If set to 1 it will be turned off. If set to 0 animal won't lose anything during movement.
    -  Energy loss per turn - an additional amount of energy lost by every animal per turn
    -  Nutritional value - specifies how much energy does an animal get frome one plant
    -  Plant spawn rate - how many plants will spawn per turn
    -  Death from hunger - if True animals will die if their energy reaches 0

Gene settings

    - Gene length - max value of a feature
    - Starting mean values - initial gene distribution will resemble normal distribution with the mean at provided value.
      - Speed - Amount of tiles an animal can go (without the base - every animal gets additional 1).
      - Attention threshold - the higher it gets, the harder it will be for an animal to be interested in something. Allows to rule out distant targets.
      - Breeding threshold - threshold of weight needed to start breeding.
      - Mutation resistance - the higher it gets, the lower chance of mutation will be.

Data export settings

    - PyGame preview - allows to watch the simulation in simple GUI created in PyGame.
    - Save JSON - Program will save data of every animal in a JSON every `n` turns.
    - Gene data is numerical - used only in summary mode, if not true program will calculate median and quarter deviation instead of mean and standard deviation.
    - CSV output modes - Summary will save population data (plant and animal amounts, energy, breeding need and gene distribution) to a CSV every `n` turns.
    - Turns between saves - data will be saved every `n-1` turns
    - CSV output - relative file directory and file name to save CSV raports.
    - JSON output - relative file directory and file name beginning to save CSV raports.
    - Information to export - values to be saved in an detailed raport. Everything from here is provided in JSONs.

Buttons:

    - Revert to default - revert to default values (pro-gamer tip: you can override `default.json` file to insert your favourite settings)
    - Save - saves the settings for future simulations
    - Start - starts the simulation. Have fun!
