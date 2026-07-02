# This file is responsible for running pygame window, calling agents, updating game state and controlling speed
# Team member responsible: Jayden

import pygame

from game.game import Game
from agents.random_agent import RandomAgent
from agents.expectimax_agent import ExpectimaxAgent
from ui.renderer import BoardRenderer, HeaderRenderer, CANVAS_COLOR
from ui.menu import run_menu

MOVE_DELAY_MS = 200

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
BOARD_OFFSET = (20, 100)

def get_agent(choice):
    if choice == "random":
        return RandomAgent()
    if choice == "expectimax":
        return ExpectimaxAgent(depth=2)

def run_game_loop(screen, agent):
    game = Game()
    board_renderer = BoardRenderer()
    header_renderer = HeaderRenderer()
    best_score = 0

    clock = pygame.time.Clock()
    last_move_time = pygame.time.get_ticks()

    running = True
    game_over = False
    restart_rect = pygame.Rect(0, 0, 0, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return True
        now = pygame.time.get_ticks()
        if not game_over and now - last_move_time >= MOVE_DELAY_MS:
            state = game.board.grid.copy()
            action = agent.choose_action(state)
            game.move(action)
            last_move_time = now

            if game.score > best_score:
                best_score = game.score

            if game.is_game_over():
                game_over = True

        screen.fill(CANVAS_COLOR)
        restart_rect = header_renderer.draw(screen, game.score, best_score)
        board_renderer.draw(screen, game.board, top_left=BOARD_OFFSET)

        pygame.display.flip()
        clock.tick(60)

    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("2048 Master")

    while True:
        choice = run_menu(screen)

        if choice is None:
            break

        agent = get_agent(choice)
        if agent is None:
            continue
        restart = run_game_loop(screen, agent)
        if not restart:
            break

    pygame.quit()

if __name__ == "__main__":
    main()