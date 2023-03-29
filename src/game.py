import logging

import pygame

import resources

class FirePlaceRock:

  def __init__(self):
    pygame.init()
    self.screen = pygame.display.set_mode()
    self.clock = pygame.time.Clock()

    self.loaded = False
    self.running = False

  def load_resources(self):
    self.sprite_bank = resources.load()
    self.loaded = True


  def run(self):
    if not self.loaded:
      logging.warning("Game is not done loading...")
      return
    self.running = True
    while self.running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False

      # fill the screen with a color to wipe away anything from last frame
      self.screen.fill("purple")
      field = pygame.transform.scale(self.sprite_bank.field, (pygame.display.Info().current_w,  pygame.display.Info().current_h))
      self.screen.blit(field, (0, 0))

      # RENDER YOUR GAME HERE
      self.sprite_bank.field

      # flip() the display to put your work on screen
      pygame.display.flip()

      self.clock.tick(60)  # limits FPS to 60

    pygame.quit()

