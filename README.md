# Hunt the Wumpus Simulation

In the following will be the possible configuration of the simulation,
as well as the controls of the simulation explained.

---

## Configuration

The Configuration of the Simulation are made in the `util/config.py` file.

### 1. Board

`GRID_SIZE = 20` The amount of cells on the x- and y-axis.\
`TILE_SIZE = 32` The amount of pixels per cell displayed.

### 2. Elements

`NUM_PITS = 20` The amount of pits per game cycle.\
`NUM_WUMPUS = 3` The amount of wumpus per game cycle.\
`NUM_GOLD = 1` The amount of gold per game cycle.

### 3. Strategy

`SHOOT = True` Whether the agents can shoot the wumpus.\
`RISKY = True` Whether the agents can enter a potential dangerous cell.\
`MANHATTEN_BONUS = True` Whether the agents try to move away from each other.

### 4. Statistic

`STATISTICS_ENABLED = True` Whether after the amount of `MAX_CYCLES` the simulation should end  
and an evaluation should be made and saved under `statistic/statistics`.\
`MAX_CYCLES = 1000` The amount of cycles, after which the simulation will end.

---

## Controls

`Enter` Toggles the game mode between two modes:
* `STEP` Makes a game step after being requested by the user.
* `CONTINUOUS` Makes a game step after a certain amount of time. 

`Space` Requests a game step, if the game mode is in `STEP`.\
`Plus` Reduces the amount of time needed for a game step, if the game mode is in `CONTINUOUS`.\
`Minus` Increases the amount of time needed for a game step, if the game mode is in `CONTINUOUS`.\
`C` Toggles between the vision of the agents and a clear vision of the gameboard.\
`R` Resets the current game cycle.\