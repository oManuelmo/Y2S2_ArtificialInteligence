import pygame
from menu import Menu
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

def game():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("FreeCell Solitaire")

    menu = Menu(screen)
    menu.menu()
    pygame.quit()

if __name__ == "__main__":
    game()