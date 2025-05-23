import pygame
from constants import RANKS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

class EventHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_free_cell_click(self, x, y):
        for i, position in enumerate((100 + i * 90, 50) for i in range(4)):
            fx, fy = position
            if fx <= x <= fx + 72 and fy <= y <= fy + 96:
                if self.game_state.freeCells[i] != "nothing":
                    self.game_state.selected_card = [self.game_state.freeCells[i]]
                    self.game_state.selected_card_pos = ("freeCell", i)
                break

    def handle_table_click(self, x, y):
        for i, column in enumerate(self.game_state.table):
            if column:
                for j in range(len(column) - 1, -1, -1):
                    card = column[j]
                    if card.rect.collidepoint(x, y) and (not card.blocked):
                        stack = [card]
                        for k in range(j + 1, len(column)):
                            stack.append(column[k])
                        if len(stack) == len(column) - j:
                            self.game_state.selected_card = stack
                        else:
                            if j == len(column) - 1:
                                self.game_state.selected_card = [card]
                            else:
                                self.game_state.selected_card = None
                        self.game_state.selected_card_pos = ("table", i, j)
                        break
                if self.game_state.selected_card:
                    break

    def handle_free_cell_drop(self, event):
        if self.game_state.selected_card:
            for i, position in enumerate((100 + i * 90, 50) for i in range(4)):
                fx, fy = position
                if fx <= event.pos[0] <= fx + 72 and fy <= event.pos[1] <= fy + 96:
                    if self.game_state.freeCells[i] == "nothing" and len(self.game_state.selected_card)==1:
                        self.game_state.move(self.game_state.selected_card_pos, self.game_state.selected_card, ("freeCell", i))
                        self.game_state.historyAppend(self.game_state.selected_card_pos, self.game_state.selected_card, ("freeCell", i))
                        self.game_state.selected_card = None
                        self.game_state.move_aces_to_foundation()
                    break

    def handle_final_cell_drop(self, event):
        if self.game_state.selected_card:
            for i, position in enumerate((530 + i * 90, 50) for i in range(4)):
                fx, fy = position
                if fx <= event.pos[0] <= fx + 72 and fy <= event.pos[1] <= fy + 96:
                    if len(self.game_state.selected_card) == 1:
                        card = self.game_state.selected_card[0]
                        if len(self.game_state.finalCells[i]) == 0:
                            if card.rank == 'ace':
                                self.game_state.move(self.game_state.selected_card_pos, self.game_state.selected_card, ("finalCell", i))
                                self.game_state.historyAppend(self.game_state.selected_card_pos, self.game_state.selected_card, ("finalCell", i))   
                                self.game_state.selected_card = None
                        else:
                            top_final_card = self.game_state.finalCells[i][-1]
                            if card.suit == top_final_card.suit and RANKS.index(card.rank) == RANKS.index(top_final_card.rank) + 1:
                                self.game_state.move(self.game_state.selected_card_pos, self.game_state.selected_card, ("finalCell", i))
                                self.game_state.historyAppend(self.game_state.selected_card_pos, self.game_state.selected_card, ("finalCell", i))   
                                self.game_state.selected_card = None
                        self.game_state.move_aces_to_foundation()
                    break

    def handle_table_drop(self, event):
        if self.game_state.selected_card:
            for i, column in enumerate(self.game_state.table):
                rect = pygame.Rect(100 + i * 100, 200 + len(column) * 20, 72, 96)
                if rect.collidepoint(event.pos):
                    if self.game_state.is_valid_move(self.game_state.selected_card, column):
                        self.game_state.move(self.game_state.selected_card_pos, self.game_state.selected_card, ("table", i))
                        self.game_state.historyAppend(self.game_state.selected_card_pos, self.game_state.selected_card, ("table", i))
                        self.game_state.selected_card = None
                        self.game_state.move_aces_to_foundation()
                    break
    
    def handle_buttons(self, event):
        x, y = event.pos
        if 100 <= x <= 150 and 650 <= y <= 700 and self.game_state.player == "Player":
            self.game_state.undo(1)
        elif 200 <= x <= 250 and 650 <= y <= 700 and self.game_state.player == "Player":
            self.game_state.show_hint()
        elif 300 <= x <= 350 and 650 <= y <= 700:
            self.game_state.restart_game()
        elif 400 <= x <= 450 and 650 <= y <= 700:
            self.game_state.newGame()
        elif 500 <= x <= 550 and 650 <= y <= 700:
            return False
        return True
    
    def handle_popup(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            popup_width = SCREEN_WIDTH // 2
            popup_height = SCREEN_HEIGHT // 2
            popup_rect = pygame.Rect(
                (SCREEN_WIDTH - popup_width) // 2,
                (SCREEN_HEIGHT - popup_height) // 2,
                popup_width,
                popup_height
            )
            
            button_font = pygame.font.Font(None, 48)
            button_padding = 20
            button_spacing = 30
            
            new_game_text = button_font.render("New Game", True, WHITE)
            restart_text = button_font.render("Restart Game", True, WHITE)
            back_text = button_font.render("Back to Menu", True, WHITE)
            
            max_text_width = max(
                new_game_text.get_width(),
                restart_text.get_width(),
                back_text.get_width()
            )
            
            button_width = max_text_width + button_padding * 2
            button_height = new_game_text.get_height() + button_padding
            
            total_buttons_height = (button_height * 3) + (button_spacing * 2)
            start_y = popup_rect.centery - total_buttons_height // 2 + 40
            
            new_game_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height
            )
            
            restart_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + button_height + button_spacing,
                button_width,
                button_height
            )
            
            back_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + (button_height + button_spacing) * 2,
                button_width,
                button_height
            )
            
            x, y = event.pos
            if new_game_rect.collidepoint(x, y):
                self.game_state.newGame()
            elif restart_rect.collidepoint(x, y):
                self.game_state.restart_game()
            elif back_rect.collidepoint(x, y):
                self.game_state.newGame()
                return False
            return True
        return True