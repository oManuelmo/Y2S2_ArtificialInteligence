import pygame
from constants import GREEN, WHITE, BLACK, SCREEN_HEIGHT, SCREEN_WIDTH
from button import Button
import sys
from game_state import GameState
from soundEffects import soundEffects
import tracemalloc

clock = pygame.time.Clock()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        button_width = 200
        button_height = 50
        spacing = 10
        total_height = 5 * button_height + 4 * spacing

        self.game_state = GameState(screen,1)

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        start_x = (screen_width - button_width) // 2
        start_y = (screen_height - total_height) // 2

        self.buttons = [
            Button("Play", start_x, start_y, button_width, button_height, self.play),
            Button("IA Simulate", start_x, start_y + (button_height + spacing), button_width, button_height, self.ai),
            Button("Choose Hint", start_x, start_y + 2 * (button_height + spacing), button_width, button_height,
                   self.choose_hint_algorithm),
            Button("Rules", start_x, start_y + 3 * (button_height + spacing), button_width, button_height,
                   self.show_rules),
            Button("Exit", start_x, start_y + 4 * (button_height + spacing), button_width, button_height,
                   self.exit_game)
        ]

    def play(self):
        self.loop("Player")
        
    def ai(self):
        self.loop("Bot")

    def loop(self, player):
        soundEffects.playMusic(0.1)
        
        if self.game_state.player != player:
            self.game_state.player = player
            self.game_state.newGame()
        else:
            self.game_state.stopTimeCalculate()
            
        running = True
        while running:
            self.screen.fill(GREEN)

            self.game_state.draw()
            if self.game_state.player == "Bot":
                self.game_state.move_bot()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    soundEffects.stopMusic()
                    sys.exit()
                    running = False
                else:
                    if self.game_state.player == "Bot":
                        check = self.game_state.handle_bot(event)
                    else:
                        check = self.game_state.handle_event(event)
                    if check == False:
                        running = False
                        self.screen.fill(GREEN)
            pygame.display.flip()
        
        soundEffects.stopMusic()
        self.game_state.startStopTime = pygame.time.get_ticks() / 1000

    def choose_hint_algorithm(self):
        button_width, button_height = 50, 50
        continue_button_width = 200
        vertical_spacing = 100
        first_row_y = SCREEN_HEIGHT // 2 - vertical_spacing
        
        buttons = [
            Button("<", 
                SCREEN_WIDTH // 2 - button_width - 250,
                first_row_y, 
                button_width, button_height, 
                self.change_minus_algorithm), 
            Button(">", 
                SCREEN_WIDTH // 2 + 250,
                first_row_y, 
                button_width, button_height, 
                self.change_plus_algorithm), 
            Button("<", 
                SCREEN_WIDTH // 2 - button_width - 250,
                first_row_y + vertical_spacing, 
                button_width, button_height, 
                self.change_minus_depth), 
            Button(">", 
                SCREEN_WIDTH // 2 + 250,
                first_row_y + vertical_spacing, 
                button_width, button_height, 
                self.change_plus_depth),
            Button("Continue", 
                SCREEN_WIDTH // 2 - continue_button_width // 2,
                first_row_y + vertical_spacing * 2 + 50, 
                continue_button_width, button_height, 
                lambda: True)
        ]
        
        self.screen.fill(GREEN)
        running = True
        
        while running:
            self.screen.fill(GREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button.check_click(event.pos):
                            running = False
            
            for button in buttons:
                button.draw(self.screen)
            
            font = pygame.font.Font(None, 36)
            
            algorithm_text = font.render(f"Algorithm: {self.game_state.algorithm}", True, WHITE)
            algorithm_x = SCREEN_WIDTH // 2 - algorithm_text.get_width() // 2
            self.screen.blit(algorithm_text, (algorithm_x, first_row_y + (button_height - algorithm_text.get_height()) // 2))
            
            depth_text = font.render(f"Depth: {self.game_state.algorithm_depth}", True, WHITE)
            depth_x = SCREEN_WIDTH // 2 - depth_text.get_width() // 2
            self.screen.blit(depth_text, (depth_x, first_row_y + vertical_spacing + (button_height - depth_text.get_height()) // 2))
            
            pygame.display.flip()
        
        self.screen.fill(GREEN)

    def goBack(self):
        return True

    def change_plus_algorithm(self):
        self.change_algorithm(1)
    
    def change_minus_algorithm(self):
        self.change_algorithm(-1)
    
    def change_plus_depth(self):
        self.change_depth(1)

    def change_minus_depth(self):
        self.change_depth(-1)

    def change_algorithm(self, direction):
        algorithms = ["DFS", "BFS", "Greedy", "Iterative Depth Search", "Uniform Cost Search", "A*Algorithm", "Weighted A*"]
        currentAlgorithm = self.game_state.algorithm
        index = algorithms.index(currentAlgorithm)
        new_index = (index + direction) % len(algorithms)
        self.game_state.algorithm = algorithms[new_index]
        self.game_state.algorithm_depth = 2

    def change_depth(self, direction):
        depth = {"DFS": (2, 5), "BFS": (2, 10), "Greedy": (2, 5), "Iterative Depth Search": (2, 5), "Uniform Cost Search": (2, 5), "A*Algorithm": (2, 5), "Weighted A*": (2, 5)}
        currentAlgorithm = self.game_state.algorithm
        currentDepth = self.game_state.algorithm_depth
        min_depth, max_depth = depth[currentAlgorithm]
        if min_depth > currentDepth + direction:
            self.game_state.algorithm_depth = max_depth
        elif max_depth < currentDepth + direction:
            self.game_state.algorithm_depth = min_depth
        else:
            self.game_state.algorithm_depth = currentDepth + direction

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def menu(self):
        running = True
        self.screen.fill(GREEN)
        self.game_state.newGame()
        while running:
           # self.screen.fill(GREEN)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        button.check_click(event.pos)
            self.draw()
            pygame.display.flip()

    def draw(self):
        # Desenhar o título do jogo
        font = pygame.font.SysFont(None, 48)  # Tamanho do texto
        title_surface = font.render("FreeCell Solitaire", True, BLACK)  # Texto em preto
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title_surface, title_rect)
        for button in self.buttons:
            button.draw(self.screen)
            
            pygame.display.flip()

    def show_rules(self):
        running = True
        font = pygame.font.SysFont(None, 24)
        rules_text = [
            "FreeCell Rules:",
            "",
            "Foundations (Four piles; upper right side of screen):",
            "- Build up in suit from Ace to King.",
            "- For example, a 2 can be played on an Ace.",
            "",
            "Cells (or Reserve: four cells, upper left):",
            "- These are the 'cells'.",
            "- Cells are storage locations for cards being played to the foundations and the tableau.",
            "- Cells can hold only one card at a time.",
            "",
            "Tableau (Eight columns, below foundations and cells):",
            "- Build down in alternating colors.",
            "- For example, a 10 can be played on a Jack.",
            "- The top card of each column is available for play to the foundations,",
            "  to another tableau column, or to the cells.",
            "- Move groups of cards if they are in sequence, and if there are enough free cells",
            "  where the cards could be moved individually.",
            "- Spaces may be filled with any card or card sequence."
        ]

        # Create the Continue button
        button_height = 50
        continue_button_width = 200
        first_row_y = 100 + len(rules_text) * 30  # Position after the last rule line
        vertical_spacing = 30
        continue_button = Button("Continue", 
                            SCREEN_WIDTH // 2 - continue_button_width // 2,
                            first_row_y + vertical_spacing - 15 , 
                            continue_button_width, button_height, 
                            lambda: True)  # Action to exit the rules screen

        while running:
            self.screen.fill(GREEN)  # Background color

            # Title
            title_font = pygame.font.SysFont(None, 36)
            title_surf = title_font.render("Game Rules", True, BLACK)
            title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(title_surf, title_rect)

            # Rules text
            for i, line in enumerate(rules_text):
                line_surface = font.render(line, True, BLACK)
                self.screen.blit(line_surface, (60, 100 + i * 30))

            # Draw the Continue button
            continue_button.draw(self.screen)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False  # Exit the rules screen and return to the main menu
                if event.type == pygame.MOUSEBUTTONUP:
                    if continue_button.check_click(event.pos):
                        running = False

            pygame.display.flip()
        self.screen.fill(GREEN)