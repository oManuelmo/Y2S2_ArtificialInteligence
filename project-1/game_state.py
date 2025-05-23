from card import Card
from constants import RANKS
import pygame
import sys

from renderer import Renderer
from event_handler import EventHandler
from hint_algorithm import get_best_move_greedy, get_best_move_dfs, get_best_move_bfs, get_best_move_ids, get_best_move_ucs, get_best_move_astar, get_best_move_weighted_astar, code_game_state, evaluate_game_state
from soundEffects import soundEffects
from utils import load_card_images, create_deck, same_color, save_bot_results
import random
import tracemalloc

class GameState:
    def __init__(self, screen, player):
        self.table = [[] for _ in range(8)]
        self.freeCells = ["nothing" for _ in range(4)]
        self.finalCells = [[] for _ in range(4)]
        self.algorithm = "Greedy"
        self.algorithm_depth = 2
        self.history = []
        self.state_history = []
        self.selected_card = None
        self.selected_card_pos = None
        self.renderer = Renderer(screen)
        self.screen = screen
        self.event_handler = EventHandler(self)
        self.message = None
        self.message_time = 0
        self.highlighted_freeCell = None
        self.highlighted_finalCell = None
        self.highlighted_emptyColumn = None
        self.last_click_time = 0
        self.player = player
        self.moving_cards_move = None
        self.start_time = pygame.time.get_ticks() / 1000
        self.score = 0
        self.stoppedTime = 0
        self.startStopTime = 0
        self.popup = 0
        self.final_time = 0
        self.seed = None
        self.hint_states = 0
        self.total_states = 0
        self.is_finished = False
    
    def stopTimeCalculate(self):
        self.stoppedTime += pygame.time.get_ticks() / 1000 - self.startStopTime
        self.startStopTime = 0

    def resetGame(self):
        self.start_time = pygame.time.get_ticks() / 1000
        self.table = [[] for _ in range(8)]
        self.freeCells = ["nothing" for _ in range(4)]
        self.finalCells = [[] for _ in range(4)]
        self.history = []
        self.state_history = []
        self.selected_card = None
        self.selected_card_pos = None
        self.score = 0
        self.is_finished = False
        self.hint_states = 0
        self.total_states = 0
        if self.player == "Bot":
            tracemalloc.start()
        
    def resetTime(self):
        self.start_time = pygame.time.get_ticks() / 1000
        self.startStopTime = 0
        self.final_time = 0

    def newGame(self):
        self.resetGame()
        self.resetTime()
        card_images = load_card_images()
        self.popup = 0
        deck = create_deck()
        self.message_time = 0
        self.startStopTime = 0
        #self.seed = 2 #CHANGE THE SEED
        #random.seed(self.seed)
        random.shuffle(deck)
        self.deal_cards(deck, card_images) # Mete as cartas no tabuleiro
        self.check_cards() # Vê as cartas blocked e unblocked
        if (self.player == "Player"):
            self.move_aces_to_foundation()

    def updateScore(self):
        score=0
        for finalCell in self.finalCells:
            score+=5*len(finalCell)
        self.score = score

    # Função para distribuir as cartas (4 grupos de 7 e 4 grupos de 6 cartas)
    def deal_cards(self, deck, card_images):
        for i in range(8):
            num_cards = 7 if i < 4 else 6
            for j in range(num_cards):
                card_name = deck.pop()
                rank, suit = card_name.split("_of_")
                card = Card(rank, suit, card_images[card_name])
                card.move(100 + i * 100, 200 + j * 20)
                self.table[i].append(card)


    # Função para ver as cartas não bloqueadas
    def check_cards(self):
        for column in self.table:
            for j in range(len(column)-1, -1, -1):
                if j == len(column) - 1:
                    column[j].blocked = False
                else:
                    # vê se a carta a seguir é 1 valor superior e de outra cor
                    if self.is_valid_sequence_from_index(column, j):
                        # Se for, a carta não está bloqueada
                        column[j].blocked = False
                    else:
                        column[j].blocked = True

    # Função para mover os Ás automaticamente para a fundação
    def move_aces_to_foundation(self):
        check_finalCells_full = True
        for finalCell in self.finalCells:
            if not finalCell:
                check_finalCells_full = False
                
        if check_finalCells_full:
            return
        # Verifica se há Ás nas colunas do tableau
        for i, column in enumerate(self.table):
            if column and column[-1].rank == 'ace':
                card = column[-1]
                for j, foundation_pile in enumerate(self.finalCells):
                    if self.is_valid_foundation_move(card, foundation_pile):
                        card.target_pos = (530 + j * 90, 50)
                        self.moving_cards_move = (("table", i, len(column) - 1), [card], ("finalCell", j))
                        
                        
                        break

        # Verifica se há Ás nas células livres
        for i, card in enumerate(self.freeCells):
            if card != "nothing" and card.rank == 'ace':
                for j, foundation_pile in enumerate(self.finalCells):
                    if self.is_valid_foundation_move(card, foundation_pile):
                        card.target_pos = (530 + j * 90, 50)
                        self.moving_cards_move = (("freeCell", i), [card], ("finalCell", j))
                        
                        break
                        
    #Função para ver se o move para a fundaçãp/finalCell é válida
    def is_valid_foundation_move(self, card, foundation_pile):
        if not foundation_pile:
            return card.rank == 'ace'
        else:
            top_card = foundation_pile[-1]
            return card.suit == top_card.suit and RANKS.index(card.rank) == RANKS.index(top_card.rank) + 1

    # Função para ver se uma sequência é válida a partir de um índice da coluna
    def is_valid_sequence_from_index(self, column, start_index):
        for j in range(start_index, len(column) - 1):
            if not self.is_valid_sequence(column[j], column[j + 1]):
                return False
        return True

    # Função para ver se duas cartas são uma sequência válida
    def is_valid_sequence(self, card1, card2):
        rank1_index = RANKS.index(card1.rank)
        rank2_index = RANKS.index(card2.rank)
        if rank2_index != rank1_index - 1:
            return False
        return not same_color(card1, card2)

    # Função para ver se o move é válido
    def is_valid_move(self, stack, target_column):
        if not target_column:
            return len(stack) <= ((self.freeCells.count("nothing") + 1) * (sum(1 for column in self.table if len(column) == 0)))
        top_card = target_column[-1]
        bottom_card = stack[0]
        return self.is_valid_sequence(top_card, bottom_card) and len(stack) <= (
                    (self.freeCells.count("nothing") + 1) * (sum(1 for column in self.table if len(column) == 0) + 1))


    # Função de handle a eventos (mouse button down e button up)
    def handle_event(self, event):
        if self.popup == 1:
            if not self.event_handler.handle_popup(event):
                return False
            return
        if event.type == pygame.MOUSEBUTTONUP:
            if (self.event_handler.handle_buttons(event) == False):
                return False
        if self.moving_cards_move:
            return
        if (self.is_game_won()):
            self.put_all_in_final_cells()
            return
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.clear_highlights()
            x, y = event.pos
            current_time = pygame.time.get_ticks()
            if current_time - self.last_click_time < 200:  # Verifica se o intervalo entre cliques é menor que 500ms
                if (self.handle_double_click(x, y)):
                    soundEffects.cardMoveSound()
            else:
                self.event_handler.handle_free_cell_click(x, y)
                if not self.selected_card:
                    self.event_handler.handle_table_click(x, y)
            self.last_click_time = current_time
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.selected_card:
                self.event_handler.handle_free_cell_drop(event)
                if self.selected_card:
                    self.event_handler.handle_final_cell_drop(event)
                if self.selected_card:
                    self.event_handler.handle_table_drop(event)
                if self.selected_card:
                    self.selected_card = None
                soundEffects.cardMoveSound()
        self.updateScore()
        return True

    # Função de handle para double click numa carta e fazer a melhor jogada
    def handle_double_click(self, x, y):
        # Verifica se a última carta de uma coluna foi clicada
        for i, column in enumerate(self.table):
            if column:
                for j in range(len(column) - 1, -1, -1):
                    card = column[j]
                    rect = pygame.Rect(100 + i * 100, 200 + j * 20, 72, 96)
                    if rect.collidepoint((x, y)):
                        if self.is_valid_sequence_from_index(column, j):
                            self.selected_card = column[j:]
                            self.selected_card_pos = ("table", i, j)
                            self.move_card_to_correct_place()
                            return

        # Verifica se uma carta em uma célula livre foi clicada
        for i, card in enumerate(self.freeCells):
            if card != "nothing":
                rect = pygame.Rect(100 + i * 100, 50, 72, 96)
                if rect.collidepoint((x, y)):
                    self.selected_card = [card]
                    self.selected_card_pos = ("freeCell", i)
                    self.move_card_to_correct_place()
                    return

    # Função que faz com que a carta se mova para o lugar certo
    def move_card_to_correct_place(self):

        if (len(self.selected_card)==1):
            # Tenta mover a carta para uma fundação
            for i, foundation_pile in enumerate(self.finalCells):
                if self.is_valid_foundation_move(self.selected_card[0], foundation_pile):
                    self.move(self.selected_card_pos, self.selected_card, ("finalCell", i))
                    self.historyAppend(self.selected_card_pos, self.selected_card, ("finalCell", i))
                    self.selected_card = None
                    if (self.player=="Player"):
                        self.move_aces_to_foundation()
                    return

        # Tenta mover a carta para uma coluna do tableau
        for i, column in enumerate(self.table):
            if not column:
                continue
            if self.is_valid_move(self.selected_card, column):
                self.move(self.selected_card_pos, self.selected_card, ("table", i))
                self.historyAppend(self.selected_card_pos, self.selected_card, ("table", i))
                self.selected_card = None
                if (self.player=="Player"):
                    self.move_aces_to_foundation()
                return
        
        if (len(self.selected_card)==1):
            # Tenta mover a carta para uma célula livre
            for i, free_cell in enumerate(self.freeCells):
                if free_cell == "nothing":
                    self.move(self.selected_card_pos, self.selected_card, ("freeCell", i))
                    self.historyAppend(self.selected_card_pos, self.selected_card, ("freeCell", i))
                    self.selected_card = None
                    if (self.player=="Player"):
                        self.move_aces_to_foundation()
                    return
        for i, column in enumerate(self.table):
            if not column:
                if self.is_valid_move(self.selected_card, column):
                    self.move(self.selected_card_pos, self.selected_card, ("table", i))
                    self.historyAppend(self.selected_card_pos, self.selected_card, ("table", i))
                    self.selected_card = None
                    if (self.player=="Player"):
                        self.move_aces_to_foundation()
                    return
        
    # Função que desenha o game_state em si
    def draw(self):
        self.renderer.draw_table_columns(self.table, self.selected_card, self.selected_card_pos, self.moving_cards_move, self.highlighted_emptyColumn)
        self.renderer.draw_free_cells(self.freeCells, self.selected_card, self.selected_card_pos, self.moving_cards_move, self.highlighted_freeCell)
        self.renderer.draw_final_cells(self.finalCells, self.highlighted_finalCell)
        self.renderer.draw_selected_cards(self.selected_card)
        self.renderer.draw_undo_button()
        self.renderer.draw_hint_button()
        self.renderer.draw_restart()
        self.renderer.draw_new_game()
        self.renderer.draw_menu_button()
        if (self.final_time == 0):
            self.renderer.draw_timer(int(pygame.time.get_ticks() / 1000 - self.start_time - self.stoppedTime))
        else: 
            self.renderer.draw_timer(int(self.final_time))
        self.renderer.draw_score(self.score)
        self.renderer.draw_moving_card(self.moving_cards_move)

        if (self.moving_cards_move):
            self.move_card()
        if (self.popup==1):
            if self.player == "Player":
                self.renderer.draw_popup(len(self.history), round(self.final_time,3))
            else:
                self.renderer.draw_popup(len(self.state_history), round(self.final_time,3))
        if self.message and self.message_timer > 0:
            self.renderer.display_message(self.message)
            self.message_timer -= 1 
        else:
            self.message = None 
    
    # Função que dá append ao histórico de moves
    def historyAppend(self, source, cards, dest):
        self.history.append((source, cards, dest))

    # Função para reverter a jogada
    def undo(self, sound):
        if len(self.history) > 0:
            if (sound==1):
                soundEffects.undoSound()
            a = self.history.pop()
            self.move(a[2], a[1], a[0])

    # Função que tira a carta do seu lugar antigo
    def remove_card_from_original_position(self, source, cards):
        if source[0] == "table":
            table_column = source[1]
            table_index = len(self.table[table_column])
            del self.table[table_column][table_index - len(cards):table_index]
        elif source[0] == "freeCell":
            self.freeCells[source[1]] = "nothing"
        elif source[0] == "finalCell":
            self.finalCells[source[1]].pop()

    # Função que faz a jogada
    def move(self, source, cards, dest):
        if dest[0] == "table":
            for card in cards:
                self.table[dest[1]].append(card)
            self.remove_card_from_original_position(source, cards)
        elif dest[0] == "freeCell":
            if self.freeCells[dest[1]] == "nothing":
                self.freeCells[dest[1]] = cards[0]
                self.remove_card_from_original_position(source, cards)
        elif dest[0] == "finalCell":
            self.finalCells[dest[1]].append(cards[0])
            self.remove_card_from_original_position(source, cards)
            
        self.check_cards()

    # Função para ver se há colunas vazias
    def has_empty_columns(self):
        for column in self.table:
            if len(column) == 0:
                return True
        return False

    # Função para encontrar todas as jogadas primárias possíveis (exceto as para freecells e colunas vazias da tabela)
    # O resultado vai ser do tipo [(("table", 0, 0), ("table", 1)), (("freeCell", 1), ("table", 3))]
    def find_all_primary_possible_moves(self):
        possible_moves = []

        # Helperzita para adicionar moves
        def add_move(source, cards, destination):
            possible_moves.append((source, cards, destination))


        # Vê os moves para as cartas da tabela
        for i, column in enumerate(self.table):
            if column:
                for j in range(len(column)):
                    card = column[j]
                    # Vê se as cartas são uma sequência válida
                    if self.is_valid_sequence_from_index(column, j) and not card.blocked:
                        # Vê se a sequência pode ir para alguma coluna da table
                        for k, target_column in enumerate(self.table):
                            if k != i and len(target_column) != 0:  # Não se mete o move para o mesmo sítio
                                if self.is_valid_move(column[j:], target_column):
                                    add_move(("table", i), column[j:], ("table", k))

                        # Vê se pode ir para uma finalCell
                        for m, foundation_pile in enumerate(self.finalCells):
                            if self.is_valid_foundation_move(card, foundation_pile) and j == len(column)-1:
                                add_move(("table", i), [card], ("finalCell", m))

        # Check moves from free cells
        for i, card in enumerate(self.freeCells):
            if card != "nothing":
                # Check if the card can be moved to a tableau column
                for j, column in enumerate(self.table):
                    if self.is_valid_move([card], column) and len(column) != 0:
                        add_move(("freeCell", i), [card], ("table", j))

                # Check if the card can be moved to a foundation pile
                for k, foundation_pile in enumerate(self.finalCells):
                    if self.is_valid_foundation_move(card, foundation_pile):
                        add_move(("freeCell", i), [card], ("finalCell", k))

        return possible_moves

    # Função para encontrar todas as jogadas secundárias possíveis (as para freeCells e colunas vazias da tabela)
    # O resultado vai ser do tipo [(("table", 0, 0), ("table", 1)), (("freeCell", 1), ("table", 3))]
    def find_all_secondary_possible_moves(self): # se for uma lista maior que 4, nao mete pras freeCells
        possible_moves = []

        # Helperzita para adicionar moves
        def add_move(source, cards, destination):
            possible_moves.append((source, cards, destination))
        
        empty_table_columns = [i for i, col in enumerate(self.table) if not col]
        if empty_table_columns:
            for i, column in enumerate(self.table):
                if column:
                    for j in range(len(column)):
                        if self.is_valid_sequence_from_index(column, j) and not column[j].blocked:
                            for empty_col in empty_table_columns:
                                if empty_col != i and self.is_valid_move(column[j:], None):
                                    add_move(("table", i), column[j:], ("table", empty_col))

            for i, card in enumerate(self.freeCells):
                if card != "nothing":
                    for empty_col in empty_table_columns:
                        add_move(("freeCell", i), [card], ("table", empty_col))

        empty_freecells = [i for i, cell in enumerate(self.freeCells) if cell == "nothing"]
        if empty_freecells:
            for i, column in enumerate(self.table):
                if column and not column[-1].blocked:
                    add_move(("table", i), [column[-1]], ("freeCell", empty_freecells[0]))

        return possible_moves

    def get_hint_best_move(self):
        best_move = None
        algorithm = self.algorithm
        self.hint_states = 0

        if self.player=="Player": tracemalloc.start()

        if algorithm == "Greedy":
            best_move = get_best_move_greedy(self, self.algorithm_depth)
        elif algorithm == "DFS":
            best_move = get_best_move_dfs(self, self.algorithm_depth)
        elif algorithm == "BFS":
            best_move = get_best_move_bfs(self, self.algorithm_depth)
        elif algorithm == "Iterative Depth Search":
            best_move = get_best_move_ids(self, self.algorithm_depth)
        elif algorithm == "Uniform Cost Search":
            best_move = get_best_move_ucs(self, self.algorithm_depth)
        elif algorithm == "A*Algorithm":
            best_move = get_best_move_astar(self, self.algorithm_depth)
        elif algorithm == "Weighted A*":
            best_move = get_best_move_weighted_astar(self, 1.5, self.algorithm_depth)

        if self.player == "Player":
            current, peak = tracemalloc.get_traced_memory()
            print(f"Memory usage for hint: {current / 1024:.2f} KB (Peak: {peak / 1024:.2f} KB)")
            tracemalloc.stop()
            print(f"States visited: {self.hint_states}")
        self.total_states += self.hint_states
        return best_move

    # Função para mostrar a melhor jogada num game_state
    def show_hint(self):
        move = self.get_hint_best_move()
        self.check_cards()
        if move:
            # Destaca a jogada
            self.highlight_move(move)
        elif "nothing" in self.freeCells or self.has_empty_columns():
            self.message = "Fill an empty cell"
            self.message_timer = 100
        else:
            self.message = "No valid moves available."
            self.message_timer = 100 

    # Função que destaca a jogada
    def highlight_move(self, move):
        source, cards, destination = move
        if source[0] == "table":
            for card in cards:
                card.highlight = True
        elif(source[0] == "freeCell"):
            index = source[1]
            card = self.freeCells[index]
            card.highlight = True

        if destination[0] == "table":
            column = destination[1]
            if self.table[column]:
                card = self.table[column][-1]
                card.highlight = True
            else:
                self.highlighted_emptyColumn = self.renderer.highlight_cell("table", destination[1])
        elif destination[0] == "freeCell":
            self.highlighted_freeCell = self.renderer.highlight_cell("freeCell", destination[1])
        elif destination[0] == "finalCell":
            index = destination[1]
            pile = self.finalCells[index]
            if len(pile) == 0: #Dá highlight à empty cell 
                self.highlighted_finalCell = self.renderer.highlight_cell("finalCell", index)
            else:
                pile[-1].highlight = True
        
    
    # Função que tira o destaque
    def clear_highlights(self):
        for column in self.table:
            for card in column:
                card.highlight = False
        for card in self.freeCells:
            if card != "nothing":
                card.highlight = False
        for pile in self.finalCells:
            if pile:
                pile[-1].highlight = False
        self.highlighted_finalCell = None
        self.highlighted_freeCell = None
        self.highlighted_emptyColumn = None

    # Função para ver se não há mais jogadas possíveis
    def is_game_over(self):
        possible_moves = self.find_all_primary_possible_moves()
        return len(possible_moves) == 0 and not ("nothing" in self.freeCells) and not self.has_empty_columns()

    def is_game_won(self):
        for column in self.table:
            for i in range(len(column) - 1):
                card1 = column[i]
                card2 = column[i + 1]
                rank1 = RANKS.index(card1.rank)
                rank2 = RANKS.index(card2.rank)
                if (rank1 <= rank2):
                    return False
        return True
    
    # Função para as cartas da table e das freeCells irem para as finalCells
    def put_all_in_final_cells(self):
        def check_if_empty_game(table, freeCells):
            for cell in freeCells:
                if cell != "nothing":
                    return False
            for column in table:
                if column:
                    return False
            return True
        
        while (not check_if_empty_game(self.table, self.freeCells)):
            for i, column in enumerate(self.table):
                if(column):
                    card = column[-1]
                    for j, foundation_pile in enumerate(self.finalCells):
                            if self.is_valid_foundation_move(card, foundation_pile):
                                card.target_pos = (530 + j * 90, 50)
                                self.moving_cards_move = (("table", i, len(column) - 1), [card], ("finalCell", j))
                                return False
            
            for i, card in enumerate(self.freeCells):
                if card != "nothing": 
                    for j, foundation_pile in enumerate(self.finalCells):
                        if self.is_valid_foundation_move(card, foundation_pile):
                            card.target_pos = (530 + j * 90, 50)
                            self.moving_cards_move = (("freeCell", i), [card], ("finalCell", j))
                            return False
        self.endGame()
        return True

    def endGame(self):
        self.popup=1
        if (self.final_time == 0):
            self.final_time = pygame.time.get_ticks()/1000 - self.start_time


    # Função para dar restart ao jogo
    def restart_game(self):
        self.is_finished = False
        self.state_history = []
        self.selected_card = None
        self.selected_card_pos = None
        self.message = None
        self.message_timer = 0
        self.popup = 0
        self.resetTime()
        while (len(self.history)>0):
            self.undo(0)
        self.check_cards()
        self.draw()
        if (self.player=="Player"):
            self.move_aces_to_foundation()

    def move_card(self):
        if self.moving_cards_move == None:
            return
        source, cards, destination = self.moving_cards_move
        first_card = cards[0]
        target_x, target_y = first_card.target_pos
        dx = target_x - first_card.rect.x
        dy = target_y - first_card.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 10:
            self.move(source, cards, destination)
            self.historyAppend(source, cards, destination)
            self.moving_cards_move = None
            if(self.is_game_won()):
                self.put_all_in_final_cells()
            if (self.player == "Player"):
                self.move_aces_to_foundation()
            self.updateScore()
            return
        for card in cards:
            target_x, target_y = card.target_pos
            dx = target_x - card.rect.x
            dy = target_y - card.rect.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            card.move(card.rect.x + dx / distance * 10, card.rect.y + dy / distance * 10)

    def handle_bot(self,event):
        if self.popup == 1:
            if not self.event_handler.handle_popup(event):
                return False
            return
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            if (self.event_handler.handle_buttons(event) == False):
                return False
    def move_bot(self):
        move = self.get_hint_best_move()
        if move:
            self.state_history.append(code_game_state(self))
            self.move(move[0], move[1], move[2])
            self.historyAppend(move[0], move[1], move[2])
        else:
            if self.all_in_final_cells():
                self.endGame()
            else:
                self.message = "No valid moves available. Try with another algorthm or depth."
                self.message_timer = 1

            if not self.is_finished:
                current, peak = tracemalloc.get_traced_memory()
                print(f"Memory usage: {current / 1024:.2f} KB (Peak: {peak / 1024:.2f} KB)")
                tracemalloc.stop()
                print(f"Total of states: {self.total_states}")
                if (self.final_time == 0):
                    self.final_time = pygame.time.get_ticks()/1000 - self.start_time
                print(f"Time (s): {round(self.final_time, 3)}")
                print(f"Total moves: {len(self.state_history)}")
                save_bot_results(self, current, peak, self.all_in_final_cells(), evaluate_game_state(self))
                self.is_finished = True

        self.updateScore()

    def all_in_final_cells(self):
        sum = 0
        for finalCell in self.finalCells:
            sum += len(finalCell)
        return sum == 52