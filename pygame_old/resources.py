import pygame
from easydict import EasyDict as edict

def load():
  sprites = edict({})

  sprites.field = pygame.image.load("../res/field/masterduel.png").convert()

  return sprites

