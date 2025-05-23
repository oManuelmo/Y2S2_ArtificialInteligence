import pygame

class soundEffects:

    def cardMoveSound():
        soundCardMove = pygame.mixer.Sound('sounds/card_move.wav')
        soundCardMove.play()

    def undoSound():
        soundUndo = pygame.mixer.Sound('sounds/undo.wav')
        soundUndo.play()

    def playMusic(volume=0.5):
        music = pygame.mixer.Sound('sounds/music.wav')
        music.set_volume(volume)
        music.play(loops=-1)

    def stopMusic():
        pygame.mixer.stop()