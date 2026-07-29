import pygame

from ui.game_loop import get_agent, run_game_loop, run_comparison
from ui.menu import run_menu

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pygame.display.set_caption("2048 Master")

    while True:
        choice = run_menu(screen)
        if choice is None:
            break
        if choice == "compare":
            if not run_comparison(screen):
                break
            continue
        agent = get_agent(choice)

        if agent is None:
            continue

        if not run_game_loop(screen, agent):
            break

    pygame.quit()

if __name__ == "__main__":
    main()
