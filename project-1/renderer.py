import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, BLACK, GRAY

class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_empty_cell(self, x, y):
        empty_cell_image = pygame.image.load('cards/empty_cell.png')
        empty_cell_image = pygame.transform.scale(empty_cell_image, (72, 96))
        self.screen.blit(empty_cell_image, (x, y))
    
    def draw_final_empty_cell(self, x, y):
        empty_cell_image = pygame.image.load('cards/final_empty_cell.png')
        empty_cell_image = pygame.transform.scale(empty_cell_image, (72, 96))
        self.screen.blit(empty_cell_image, (x, y))

    def draw_table_columns(self, table, selected_card, selected_card_pos, moving_cards_move, highlighted_rect):
        for i, column in enumerate(table):
            isEmpty = True
            if column:
                for j, card in enumerate(column):
                    if selected_card and selected_card_pos[0] == "table" and selected_card_pos[1] == i and selected_card_pos[2] <= j < selected_card_pos[2] + len(selected_card):
                        continue
                    if moving_cards_move and moving_cards_move[0][0] == "table" and moving_cards_move[0][1] == i and moving_cards_move[0][2] <= j<moving_cards_move[0][2] + len(moving_cards_move[1]):
                        continue
                    card.draw(self.screen, 100 + i * 100, 200 + j * 20)
                    isEmpty = False
            if isEmpty:
                self.draw_empty_cell(100 + i * 100, 200)
        if highlighted_rect:
            pygame.draw.rect(self.screen, (255, 255, 0), highlighted_rect, 3)

    def draw_free_cells(self, freeCells, selected_card, selected_card_pos, moving_cards_move, highlighted_rect):
        for i, position in enumerate((100 + i * 90, 50) for i in range(4)):
            x, y = position
            if freeCells[i] == "nothing":
                self.draw_empty_cell(x, y)
            else:
                if selected_card and selected_card_pos[0] == "freeCell" and selected_card_pos[1] == i:
                    self.draw_empty_cell(x, y) 
                    continue
                if moving_cards_move and moving_cards_move[0][0] == "freeCell" and moving_cards_move[0][1] == i:
                    self.draw_empty_cell(x, y) 
                    continue
                card = freeCells[i]
                card.draw(self.screen, x, y)
        if highlighted_rect:
            pygame.draw.rect(self.screen, (255, 255, 0), highlighted_rect, 3)

    def draw_final_cells(self, final_cells, highlighted_rect):
        for i, position in enumerate((530 + i * 90, 50) for i in range(4)):
            x, y = position
            if len(final_cells[i]) == 0:
                self.draw_final_empty_cell(x, y)
            else:
                card = final_cells[i][-1]
                card.draw(self.screen, x, y)
        if highlighted_rect:
            pygame.draw.rect(self.screen, (255, 255, 0), highlighted_rect, 3)

    def draw_selected_cards(self, selected_card):
        if selected_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i, card in enumerate(selected_card):
                card.draw(self.screen, mouse_x - 36, mouse_y - 25 + i * 20)

    def draw_moving_card(self, moving_cards_move):
        if moving_cards_move:
            for card in moving_cards_move[1]:
                card.draw(self.screen, card.rect.x, card.rect.y)

    def draw_timer(self, elapsed_time):
        if (elapsed_time<0):
            elapsed_time=0
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = f"{minutes:02}:{seconds:02}"
        font = pygame.font.Font(None, 36)
        text = font.render(timer_text, True, (255, 255, 255))
        self.screen.blit(text, (30, 30))

    def draw_score(self, score):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        text_width = text.get_width()
        self.screen.blit(text, (SCREEN_WIDTH - text_width - 30, 30))
        
        
    def draw_undo_button(self):
        undo_button_image = pygame.image.load('cards/undo_button.png')
        undo_button_image = pygame.transform.scale(undo_button_image, (50, 50))
        self.screen.blit(undo_button_image, (100, 650))

    def draw_hint_button(self):
        hint_button_image = pygame.image.load('cards/hint_button.png')
        hint_button_image = pygame.transform.scale(hint_button_image, (50, 50))
        self.screen.blit(hint_button_image, (200, 650))
    
    def draw_restart(self):
        restart_button_image = pygame.image.load('cards/restart.png')
        restart_button_image = pygame.transform.scale(restart_button_image, (50, 50))
        self.screen.blit(restart_button_image, (300, 650))

    def display_message(self, message):
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(text, text_rect)
    
    def highlight_cell(self, cell_type, index):
        if cell_type == "finalCell":
            x, y = 530 + index * 90, 50
            return pygame.Rect(x, y, 72, 96)
        elif cell_type == "freeCell":
            x, y = 100 + index * 90, 50
            return pygame.Rect(x, y, 72, 96)
        else:
            x, y = 100 + index * 100, 200
            return pygame.Rect(x, y, 72, 96)
    
    def draw_new_game(self):
        restart_button_image = pygame.image.load('cards/new_game.png')
        restart_button_image = pygame.transform.scale(restart_button_image, (50, 50))
        self.screen.blit(restart_button_image, (400, 650))

    def draw_menu_button(self):
        restart_button_image = pygame.image.load('cards/menu_button.png')
        restart_button_image = pygame.transform.scale(restart_button_image, (50, 50))
        self.screen.blit(restart_button_image, (500, 650))
    
    def draw_popup(self, total_moves, time_elapsed):
        popup_width = SCREEN_WIDTH // 2
        popup_height = SCREEN_HEIGHT // 2
        popup_rect = pygame.Rect(
            (SCREEN_WIDTH - popup_width) // 2,
            (SCREEN_HEIGHT - popup_height) // 2,
            popup_width,
            popup_height
        )
        pygame.draw.rect(self.screen, (230, 230, 230), popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, (180, 180, 180), popup_rect, 2, border_radius=10)

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("YOU WON!", True, GREEN)
        self.screen.blit(title_text, (
            SCREEN_WIDTH // 2 - title_text.get_width() // 2,
            popup_rect.y + 30 
        ))

        stats_font = pygame.font.Font(None, 28)
        moves_text = stats_font.render(f"Moves: {total_moves}", True, BLACK)

        time_text = stats_font.render(f"Time (s): {time_elapsed}", True, BLACK)

        self.screen.blit(moves_text, (
            SCREEN_WIDTH // 2 - time_text.get_width() // 2 + 150,
            popup_rect.y + 350
        ))
        self.screen.blit(time_text, (
            SCREEN_WIDTH // 2 - time_text.get_width() // 2 - 150,
            popup_rect.y + 350
        ))

        button_font = pygame.font.Font(None, 48)
        button_color = GRAY
        button_border = (150, 150, 150)
        button_padding = 20
        button_spacing = 30
        
        # Determine the widest button text
        new_game_text = button_font.render("New Game", True, BLACK)
        restart_text = button_font.render("Restart Game", True, BLACK)
        back_text = button_font.render("Back to Menu", True, BLACK)
        
        max_text_width = max(
            new_game_text.get_width(),
            restart_text.get_width(),
            back_text.get_width()
        )
        
        button_width = max_text_width + button_padding * 2
        button_height = new_game_text.get_height() + button_padding
        
        # Calculate positions (moved buttons lower by adding 40 to start_y)
        total_buttons_height = (button_height * 3) + (button_spacing * 2)
        start_y = popup_rect.centery - total_buttons_height // 2 + 40  # Added +40 to move lower
        
        # New Game button
        new_game_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, button_color, new_game_rect, border_radius=8)
        pygame.draw.rect(self.screen, button_border, new_game_rect, 2, border_radius=8)
        self.screen.blit(new_game_text, (
            new_game_rect.centerx - new_game_text.get_width() // 2,
            new_game_rect.centery - new_game_text.get_height() // 2
        ))
        
        # Restart Game button
        restart_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, button_color, restart_rect, border_radius=8)
        pygame.draw.rect(self.screen, button_border, restart_rect, 2, border_radius=8)
        self.screen.blit(restart_text, (
            restart_rect.centerx - restart_text.get_width() // 2,
            restart_rect.centery - restart_text.get_height() // 2
        ))
        
        # Back to Menu button
        back_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + (button_height + button_spacing) * 2,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, button_color, back_rect, border_radius=8)
        pygame.draw.rect(self.screen, button_border, back_rect, 2, border_radius=8)
        self.screen.blit(back_text, (
            back_rect.centerx - back_text.get_width() // 2,
            back_rect.centery - back_text.get_height() // 2
        ))