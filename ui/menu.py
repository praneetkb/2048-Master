# This file is responsible for logic of the menu
# It allows user to select between the agents (expectimax, random, RL)
# Team member responsible: Ryan

import pygame 
from ui.renderer import MenuRenderer

# K_1 is the '1' key on keyboard
CHOICES = {
    pygame.K_1: "random",
    pygame.K_2: "expectimax",
    pygame.K_3: "rl_agent",
    pygame.K_4: "compare",
}

CHOICE_ORDER = ["random", "expectimax", "rl_agent", "compare",]

#menu loop
def run_menu(screen):
    renderer = MenuRenderer()
    clock = pygame.time.Clock()

    button_rects = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        hovered_index = None
        for index, rect in enumerate(button_rects):
            if rect.collidepoint(mouse_pos):
                hovered_index = index
                break
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key in CHOICES:
                return CHOICES[event.key]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_index is not None:
                    return CHOICE_ORDER[hovered_index]

        button_rects = renderer.draw(screen, hovered_index=hovered_index)
        pygame.display.flip()
        #loop runs 60fps
        clock.tick(60)



