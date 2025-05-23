import math
from collections import deque
import heapq
from utils import same_color

# Função que calcula a pontuação de uma game_state para ajudar a escolher a melhor jogada
def evaluate_game_state(game_state):
    if code_game_state(game_state) in game_state.state_history:
            return -math.inf
    score = 0
    score += (game_state.freeCells.count("nothing") + 1) * (sum(1 for column in game_state.table if len(column) == 0) + 1)*1000

    # Prioridade 1: Cartas na finalCells
    for foundation in game_state.finalCells:
        score += len(foundation) * 200  


    # Priority 3: O jogo que tiver mais cartas desbloqueadas
    for column in game_state.table:
        for i, card in enumerate(column):
            if not card.blocked:
                score += 10
            else:
                score -= 20*(len(column)-i)

    return score

# Check (DFS) para ver se o move leva a um loop infinito se sim retorna True. Basta um depth de 2
def check_has_loop(game_state, move, initial_state, is_secondary=False, depth=1):
    source, cards, destination = move

    game_state.move(source, cards, destination)
    state_code = code_game_state(game_state)
    if state_code in game_state.state_history:
        game_state.move(destination, cards, source)
        return False
    if state_code == initial_state:
        game_state.move(destination, cards, source)
        return True

    # Se chegar ao fim então quer dizer que não encontrou para este lado
    if depth == 0:
        game_state.move(destination, cards, source)
        return False

    possible_moves = game_state.find_all_primary_possible_moves()
    if is_secondary:
        possible_moves += game_state.find_all_secondary_possible_moves()
    for next_move in possible_moves:
        if check_has_loop(game_state, next_move, initial_state, is_secondary, depth - 1):
            game_state.move(destination, cards, source)
            return True

    game_state.move(destination, cards, source)
    return False

# Função code para cada game_state. Serve para nao estar a guardar a game_state toda para nao ficar pesado e para poder ser mais facil de comparar
def code_game_state(game_state): 
    state_str = ""

    for column in game_state.table:
        for card in column:
            state_str += f"{card.rank}_{card.suit}_"
        state_str += "|"

    for cell in game_state.freeCells:
        if cell == "nothing":
            state_str += "empty_"
        else:
            state_str += f"{cell.rank}_{cell.suit}_"
    state_str += "|"

    for foundation in game_state.finalCells:
        for card in foundation:
            state_str += f"{card.rank}_{card.suit}_"
        state_str += "|"

    return state_str

# Função para maximizar a jogada com um limite de profundidade de pesquisa
def maximize_primary(game_state, depth, initial_state, alpha=-math.inf, beta=math.inf, best_move=None):
    game_state.hint_states += 1
    if depth == 0 or game_state.is_game_over():
        return evaluate_game_state(game_state), best_move

    max_eval = -math.inf
    current_best_move = None
    possible_moves = game_state.find_all_primary_possible_moves()

    possible_moves.sort(key=lambda move: estimate_move_quality(move, game_state), reverse=True)

    for move in possible_moves:
        # Prune se tiver loop
        if check_has_loop(game_state, move, initial_state):
            continue

        source, cards, destination = move

        #  Caso o jogo esteja ganho basta retornar uma jogada válida qualquer para a foundation
        if game_state.is_game_won() and destination[0] == "finalCell":
            return math.inf, move
        
        if len(cards) == 1 and cards[0].rank == "ace" and destination[0] == "finalCell":
            return math.inf, move

        game_state.move(source, cards, destination)

        # Prune se for uma jogada repetida
        if code_game_state(game_state) in game_state.state_history:
            game_state.move(destination, cards, source)
            continue
        
        eval, _ = maximize_primary(game_state, depth-1, initial_state, alpha, beta, move)
        
        game_state.move(destination, cards, source)

        if eval > max_eval:
            max_eval = eval
            current_best_move = move
            alpha = max(alpha, eval)
            # Prune caso a jogada seja a melhor possível (neste caso so vai acontecer se for um ás para a foundation ou o jogo estiver "ganho")
            if beta <= alpha:
                break

    return max_eval, current_best_move

# Função para ver se a jogada secundária é trivial
def check_trivial_secondary_move(game_state, move):
    is_trivial = False
    source, cards, destination = move
    if len(cards) == 1 and destination[0] == "freeCell":
        the_card = cards[0]
        for card in game_state.freeCells:
            if card != "nothing" and card.rank == the_card.rank and same_color(card, the_card) and len(game_state.table[source[1]]) != 1 and not game_state.table[source[1]][-len(cards)].blocked:
                is_trivial = True
    # Vê se o move é de cartas todas de uma coluna para uma coluna vazia
    if source[0] == "table" and destination[0]== "table" and not game_state.table[destination[1]] and len(game_state.table[source[1]]) == len(cards):
        is_trivial = True
        
    return is_trivial

def maximize_secondary(game_state, initial_state, depth=2):
    game_state.hint_states += 1
    possible_moves = game_state.find_all_secondary_possible_moves()
    best_eval = -math.inf
    best_move = None
    possible_moves.sort(key=lambda move: estimate_move_quality(move, game_state), reverse=True)

    for move in possible_moves:
        if check_trivial_secondary_move(game_state, move):
            continue

        if check_has_loop(game_state, move, initial_state, True):
            continue
        
        source, cards, destination = move
        game_state.move(source, cards, destination)
        if code_game_state(game_state) in game_state.state_history:
            game_state.move(destination, cards, source)
            continue
        eval, _ = maximize_primary(game_state, 2, initial_state)
        game_state.move(destination, cards, source)
        if (best_eval< eval):
            best_eval = eval
            best_move = move

    # caso nao tneha best move, mete-se mais um move secundário e vê se se tem algum primário, senão realiza-se mais uma vez
    if not best_move and possible_moves:
        for move in possible_moves:
            if check_trivial_secondary_move(game_state, move):
                continue
            source, cards, destination = move
            game_state.move(source, cards, destination)
            if code_game_state(game_state) in game_state.state_history:
                game_state.move(destination, cards, source)
                continue
            eval, _ = maximize_secondary(game_state, initial_state, depth-1)
            game_state.move(destination, cards, source)
            if (best_eval< eval):
                best_eval = eval
                best_move = move
    return best_eval, best_move

# Estima a qualidade da jogada (ajuda a escolher qual a melhor ordenando os possible moves)
def estimate_move_quality(move, game_state):
    source, cards, destination = move
    score = 0
    if destination[0] == "table" and not game_state.table[destination[1]]:
        score+=10 *len(cards)

    if destination[0] == "finalCell":
        score += 100 * len(cards)

    if source[0] == "table" and len(cards) > 1:
        score += 10 * len(cards)
    
    if source[0] == "table" and len(game_state.table[source[1]]) == len(cards):
        score += 50
    
    if source[0] == "freeCell":
        score +=100

    return score

# Função principal do ficheiro: encontra a melhor jogada heuristicamente
def get_best_move_greedy(game_state, depth=3):
    possible_moves = game_state.find_all_primary_possible_moves()
    best_move = None
    initial_state = code_game_state(game_state)
    if possible_moves:
        _, best_move = maximize_primary(game_state, depth, initial_state)
        # Caso o maximizador não encontrar nenhum, damos ao best_move um qualquer
        if best_move == None:
            best_move = possible_moves[0]
        # Vê se encontramos um move que não tenha loop para nao ficar la infinitamente
        if (check_has_loop(game_state, best_move, initial_state)):
            best_move = None
            for move in possible_moves:
                if (not check_has_loop(game_state, move, initial_state)):
                    best_move = move
                    break

    if best_move == None:
        _, best_move = maximize_secondary(game_state, initial_state)
    return best_move

# Função para conseguir a melhor jogada por DFS
def get_best_move_dfs(game_state, max_depth=3):
    best_score = -math.inf
    best_move = None
    visited = set()
    
    def dfs(state, depth, path):
        game_state.hint_states += 1
        nonlocal best_score, best_move
        
        current_state_code = code_game_state(state)
        if current_state_code in visited or depth > max_depth:
            return
        visited.add(current_state_code)
        
        if state.is_game_over():
            best_move = path[0] if path else None
            best_score = math.inf
            return
            
        current_score = evaluate_game_state(state)
        if current_score > best_score and path:
            best_score = current_score
            best_move = path[0]
            
        possible_moves = state.find_all_primary_possible_moves() + state.find_all_secondary_possible_moves()
        for move in possible_moves:
            source, cards, destination = move
            state.move(source, cards, destination)
            if code_game_state(game_state) in game_state.state_history:
                game_state.move(destination, cards, source)
                continue
            dfs(state, depth + 1, path + [move])
            state.move(destination, cards, source)
    
    dfs(game_state, 0, [])
    
    return best_move

# Função para conseguir a melhor jogada por BFS
def get_best_move_bfs(game_state, max_depth=3):
    queue = deque()
    visited = set()
    best_score = -math.inf
    best_move = None
    
    initial_state_code = code_game_state(game_state)
    queue.append((0, None))  # (depth, first_move)
    visited.add(initial_state_code)
    
    while queue:
        depth, first_move = queue.popleft()

        game_state.hint_states += 1

        current_score = evaluate_game_state(game_state)
        if current_score > best_score and first_move is not None:
            best_score = current_score
            best_move = first_move
            
        if game_state.is_game_over():
            return first_move
            
        if depth >= max_depth:
            continue
            
        possible_moves = game_state.find_all_primary_possible_moves() + game_state.find_all_secondary_possible_moves()
        
        for move in possible_moves:
            source, cards, destination = move
            game_state.move(source, cards, destination)
            new_state_code = code_game_state(game_state)
            if new_state_code not in visited and new_state_code not in game_state.state_history:
                visited.add(new_state_code)
                new_first_move = first_move if first_move is not None else move
                queue.append((depth + 1, new_first_move))

            game_state.move(destination, cards, source)

    return best_move

# Função para conseguir a melhor jogada por Ierative Depth Search
def get_best_move_ids(game_state, max_depth=3):
    best_move = None
    best_eval = -math.inf
    for depth_limit in range(1, max_depth + 1):
        current_move = get_best_move_dfs(game_state, depth_limit)
        if current_move:
            current_eval = evaluate_game_state(game_state)
            if current_eval> best_eval:
                best_move = current_move
                best_eval = evaluate_game_state(game_state)
            if best_eval == math.inf:
                break
    
    return best_move

# Função para conseguir a melhor jogada por Uniform cost
def get_best_move_ucs(game_state, max_depth= 2):
    heap = []
    visited = set()
    
    initial_state = code_game_state(game_state)
    heapq.heappush(heap, (0, 0, initial_state, []))
    
    best_score = -math.inf
    best_move = None
    all_move_sequences = {}
    
    while heap:
        _, move_count, state_code, move_indices = heapq.heappop(heap)
        game_state.hint_states += 1
        if move_count > max_depth:
            continue

        if state_code in visited: # Dá skip se estiver visitado
            continue
        visited.add(state_code)
        
        move_sequence = all_move_sequences.get(tuple(move_indices), []) # Pega-se a sequência de jogadas
        
        for move in move_sequence: # Realiza a sequência de jogadas
            source, cards, destination = move
            game_state.move(source, cards, destination)
        
        current_score = evaluate_game_state(game_state) # Avalia o game_state
        if current_score > best_score and move_sequence: # Se for melhor, então troca-se
            best_score = current_score
            best_move = move_sequence[0]
            
        if game_state.is_game_won(): # Se ganhar, dá undo às jogadas feitas e returna a primeira jogada da sequência
            for move in reversed(move_sequence):
                source, cards, destination = move
                game_state.move(destination, cards, source)
            break
            
        if game_state.is_game_over(): # Se perder, dá undo às jogadas e continua com uma nova sequência
            for move in reversed(move_sequence):
                source, cards, destination = move
                game_state.move(destination, cards, source)
            continue
            
        # Pega todas as jogadas válidas e dá lhes índices
        possible_moves = game_state.find_all_primary_possible_moves() + game_state.find_all_secondary_possible_moves()
        for move_idx, move in enumerate(possible_moves):
            source, cards, destination = move
            #if check_trivial_secondary_move(game_state,move):
            #    continue
            game_state.move(source, cards, destination)
            if code_game_state(game_state) in game_state.state_history:
                game_state.move(destination, cards, source)
                continue
            new_state_code = code_game_state(game_state) # Cria um state code
            new_move_indices = move_indices + [move_idx] # Cria-se a nova lista de move_indices
            new_cost = move_count + 1 # O custo é +1
            
            new_move_sequence = move_sequence + [move] # Cria-se uma nova sequência de jogadas com o novo move adicionado
            all_move_sequences[tuple(new_move_indices)] = new_move_sequence # Guarda a sequência de jogadas
            
            game_state.move(destination, cards, source)
            
            # Dá push apenas às indices (ao meter o move, estava a dar erro)
            heapq.heappush(heap, (new_cost, new_cost, new_state_code, new_move_indices))
        
        # Dá undo às jogads para voltar à state original
        for move in reversed(move_sequence):
            source, cards, destination = move
            game_state.move(destination, cards, source)

    if game_state.is_game_won():
        possible_moves = game_state.find_all_primary_possible_moves()
        for move in possible_moves:
            if move[2][0] == "finalCell":
                return move

    return best_move

# Função para conseguir a melhor jogada por astar (código base para as duas heurísticas abaixo)
def base_astar_search(game_state, weight=1.0, depth_limit=10):
    open_set = []
    visited = set()
    
    initial_state = code_game_state(game_state)
    initial_move_hash = hash(str([]))
    heapq.heappush(open_set, 
                 (weight * evaluate_game_state(game_state),   # f-score
                  0,                                # g-score
                  initial_state,
                  initial_move_hash,                # Hash de sequência vazia de jogadas
                  None))
    
    move_sequences = {initial_move_hash: []}
    best_score = -math.inf
    best_move = None
    
    while open_set:
        current_f, g_score, state_code, move_hash, _ = heapq.heappop(open_set)
        
        game_state.hint_states += 1

        if state_code in visited:
            continue
        visited.add(state_code)
        
        move_sequence = move_sequences[move_hash]
        
        # Faz as jogadas da sequência
        for move in move_sequence:
            source, cards, destination = move
            game_state.move(source, cards, destination)
        
        # Avalia o jogo, se for bom então troca-se
        current_score = evaluate_game_state(game_state)
        if current_score > best_score and move_sequence:
            best_score = current_score
            best_move = move_sequence[0]


        if game_state.is_game_won():
            for move in reversed(move_sequence):
                source, cards, destination = move
                game_state.move(destination, cards, source)
            break

        if game_state.is_game_over() or len(move_sequence) >= depth_limit:
            # Undo moves
            for move in reversed(move_sequence):
                source, cards, destination = move
                game_state.move(destination, cards, source)
            continue
            
        # Processa as jogadas
        possible_moves = game_state.find_all_primary_possible_moves() + game_state.find_all_secondary_possible_moves()
        for move in possible_moves:
            source, cards, destination = move
            if check_trivial_secondary_move(game_state,move):
                continue
            game_state.move(source, cards, destination)
            if code_game_state(game_state) in game_state.state_history:
                game_state.move(destination, cards, source)
                continue
            
            new_state_code = code_game_state(game_state)
            new_move_sequence = move_sequence + [move]
            new_move_hash = hash(str(new_move_sequence))
            new_g_score = g_score + 1
            new_f_score = new_g_score + weight * evaluate_game_state(game_state)
            
            move_sequences[new_move_hash] = new_move_sequence
            game_state.move(destination, cards, source)
            
            if new_state_code not in visited:
                heapq.heappush(open_set, 
                              (new_f_score,
                               new_g_score,
                               new_state_code,
                               new_move_hash,
                               None))
        
        # Undo all moves
        for move in reversed(move_sequence):
            source, cards, destination = move
            game_state.move(destination, cards, source)
    
    if game_state.is_game_won():
        possible_moves = game_state.find_all_primary_possible_moves()
        for move in possible_moves:
            if move[2][0] == "finalCell":
                return move

    return best_move

# Função para conseguir a melhor jogada por A*
def get_best_move_astar(game_state, depth):
    return base_astar_search(game_state, weight=1.0, depth_limit = depth)

# Função para conseguir a melhor jogada por Weighted A*
def get_best_move_weighted_astar(game_state, depth, weight=1.5):
    return base_astar_search(game_state, weight=weight, depth_limit = depth)

