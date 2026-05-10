import pygame

LOC = 'assets/sprites/'

dang = {}

def load_image(path):
    if path not in dang:
        img = pygame.image.load(LOC + path).convert_alpha()
        dang[path] = img
    return dang[path]



