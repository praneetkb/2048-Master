# This file is responsible for logic of the menu
# It allows user to select between the agents (expectimax, random, RL)
# Team member responsible: Ryan

import pygame 
from ui.renderer import MenuRenderer

# K_1 is the '1' key on keyboard
CHOICES = {
    pygame.K_1: "random",
    pygame.K_2: "expectimax",
    pygame.K_3: "RL",
}

#menu loop
def run_menu(screen):

    # this returns "random","expectimax" or "RL"
    renderer = MenuRenderer()
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key in CHOICES:
                return CHOICES[event.key]

            renderer.draw(screen)
            pygame.display.flip()
            #loop runs 60fps
            clock.tick(60)



