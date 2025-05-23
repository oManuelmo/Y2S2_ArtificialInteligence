import pygame

class Card:
    def __init__(self, rank, suit, image):
        self.rank = rank
        self.suit = suit
        self.image = image
        self.rect = self.image.get_rect()
        self.highlight = False
        self.blocked = True

    def move(self, x, y):
        self.rect.topleft = (x, y)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.image, self.rect)
        if self.blocked: 
            dark_overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 128)) # 50% de opacidade
            screen.blit(dark_overlay, self.rect.topleft)
        if self.highlight:
            # Se for dastacada, desenhar com uma borda
            pygame.draw.rect(screen, (255, 255, 0), self.rect, 3)