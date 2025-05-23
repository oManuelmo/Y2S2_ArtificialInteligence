import pygame
import os
from constants import RANKS, SUITS
from datetime import datetime

def load_card_images():
    images = {}
    for suit in SUITS:
        for rank in RANKS:
            image = pygame.image.load(os.path.join("cards", f"{rank}_of_{suit}.png"))
            images[f"{rank}_of_{suit}"] = pygame.transform.scale(image, (72, 96))
    return images

def create_deck():
    return [f"{rank}_of_{suit}" for suit in SUITS for rank in RANKS]

def same_color(card1, card2):
    red_suits = ['hearts', 'diamonds']
    card1_color = 'red' if card1.suit in red_suits else 'black'
    card2_color = 'red' if card2.suit in red_suits else 'black'
    return card1_color == card2_color

def save_bot_results(game_state, memory, peak, has_won, value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_moves = len(game_state.state_history)
    elapsed_time = game_state.final_time
    total_states = game_state.total_states
    with open("results.txt", "a") as f: 
        f.write("\n" + "="*50 + "\n")
        f.write(f"Test performed at: {timestamp}\n")
        f.write("-"*50 + "\n")
        if game_state.seed:
            f.write(f'Seed tested: {game_state.seed}\n')
            f.write("-"*50 + "\n")
        f.write(f"Has won: {has_won}\n")
        f.write(f"Final game_state value: {value}\n")
        f.write(f"{'Algorithm:':<20} {game_state.algorithm}\n")
        f.write(f"{'Search depth:':<20} {game_state.algorithm_depth}\n")
        f.write(f"{'Time elapsed:':<20} {elapsed_time:.2f} seconds\n")
        f.write(f"{'Total moves:':<20} {total_moves}\n")
        f.write(f"{'Memory used:':<20} {memory/1024:.2f} KB\n")
        f.write(f"{'Peak memory used:':<20} {peak/1024:.2f} KB\n")
        f.write(f"{'States evaluated:':<20} {game_state.total_states}\n")
        f.write("-"*50 + "\n")
        f.write(f"{'Moves per second:':<20} {total_moves/elapsed_time:.2f}\n")
        f.write(f"{'States per second:':<20} {total_states/elapsed_time:.7f}\n")
        f.write(f"{'KB per state:':<20} {(memory/1024)/max(1,total_states):.4f}\n")
        f.write("="*50 + "\n")