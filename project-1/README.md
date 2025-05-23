# FreeCell Solitaire

## How to compile
1. You will need to install [Python3](https://www.python.org/downloads/)
2. You will need the [pygame](https://www.pygame.org/wiki/)

```shell
pip install pygame
```

## How to change the seed
- In lines **80** and **81** of the file `game_state.py`, you can change the seed of the game.

## How ro run
- In a Python IDE, in the main.py file:
    -  press run.  

- In the command line, for windows, in the src directory:
```shell
python main.py
```  

- In the command line, for linux, in the src directory:
```shell
python3 main.py
```  
## How to use
1. **Play**
   - Starts the game in Player mode.
2. **IA Simulate**
   - To Start the game in AI and it will store the results after game ended.
3. **Choose Hint**
   - Allows you to select the hint algorithm and search depth.
   - **Depth**: Adjust the search depth for algorithms that support this configuration.
   - Use the "<" and ">" buttons to switch between algorithms and adjust the depth.
4. **Rules**
   - Displays the rules of FreeCell Solitaire.
   - Includes explanations about the foundations, free cells, and tableau.
5. **Exit**
   - Closes the game.


### Gameplay Instructions
1. **Starting the Game**:
   - Select "Play" to start the game in Player mode or "IA Simulate" for AI mode.
   - The game board will display the tableau (8 columns), free cells (4 slots), and foundation piles (4 slots).

2. **Moving Cards**:
   - **Drag and Drop**: Use your mouse to drag and drop cards between tableau columns, free cells, and foundation piles.
   - **Double Click**: Double click a card to automatically move it to the best possible position.

3. **Rules**:
   - Cards in the tableau must be placed in descending order and alternate colors.
   - Free cells can hold one card each and can be used as temporary storage.
   - Cards can only be moved to the foundation piles if they follow the correct suit and rank order.

4. **Hints**:
   - Click the "Hint" button to highlight the best possible move based on the selected algorithm.

5. **Restarting or Starting a New Game**:
   - Use the "Restart" button to reset the current game while keeping the same card layout.
   - Use the "New Game" button to shuffle the deck and start a new game.

6. **Winning the Game**:
   - The game is won when all cards are moved to the foundation piles in the correct order.

### Scoring
- Points are awarded for moving cards to the foundation piles:
  - Each card moved to a foundation pile earns 5 points.
- The score is displayed on the screen during gameplay.
