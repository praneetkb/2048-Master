import pygame
import time

from ui.renderer import BoardRenderer, HeaderRenderer, MenuRenderer

pygame.init()

screen = pygame.display.set_mode((700, 700))
pygame.display.set_caption("UI Live Test")

board_renderer = BoardRenderer()
header_renderer = HeaderRenderer()
menu_renderer = MenuRenderer()

# fake game data
board = [
    [2, 4, 8, 16],
    [32, 64, 128, 256],
    [512, 1024, 2048, 0],
    [0, 0, 0, 0],
]

state = "game" # can change to "menu" to test menu rendering

show_menu = True
running = True

start_time = time.time()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_menu = not show_menu

    screen.fill((250, 248, 239))

    if state == "menu":
        menu_renderer.draw(screen)
    else:
        header_renderer.draw(screen, score=1234, best_score=5678)
        board_renderer.draw(screen, board, top_left=(20, 100))

    pygame.display.flip()

    # auto close after 60 seconds (so tests don't hang forever)
    if time.time() - start_time > 60:
        running = False

pygame.quit()