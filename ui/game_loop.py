# This file is responsible for running pygame window, calling agents, updating game state and controlling speed
# Team member responsible: Jayden

import pygame
from pathlib import Path
from agents.n_tuple_network import NTupleNetwork
from agents.expectimax_rl_agent import ExpectimaxRLAgent
from agents.random_agent import RandomAgent
from game.game import Game
from ui.menu import run_menu
from ui.renderer import CANVAS_COLOR, BoardRenderer, HeaderRenderer
from ui.animation import TileAnimator

POST_MOVE_PAUSE_MS = 120

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
BOARD_OFFSET = (20, 100)

def get_agent(choice):
    if choice == "random":
        return RandomAgent()
    if choice == "expectimaxRL":
        checkpoint = Path("checkpoints/value_function.npz")
        if checkpoint.exists():
            print("Loaded trained value function")
            return ExpectimaxRLAgent(depth=2, network=NTupleNetwork.load(checkpoint))
        print("No checkpoint found, using the heuristic evaluation")
        return ExpectimaxRLAgent(depth=2)

def run_game_loop(screen, agent):
    game = Game()
    board_renderer = BoardRenderer()
    header_renderer = HeaderRenderer()
    animator = TileAnimator()
    animator.snapshot(game.board.grid)
    best_score = 0

    clock = pygame.time.Clock()
    idle_time = 0

    running = True
    game_over = False
    restart_rect = pygame.Rect(0, 0, 0, 0)

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return True
        animator.update(dt)
        if animator.is_animating():
            idle_time = 0
        else:
            idle_time += dt

        if not game_over and not animator.is_animating() and idle_time >= POST_MOVE_PAUSE_MS:
            old_grid = game.board.grid.copy()
            action = agent.choose_action(old_grid)
            changed = game.move(action)

            if changed:
                animator.start_move(old_grid, action, game.board.grid)
            
                if game.score > best_score:
                    best_score = game.score

            idle_time = 0

            if game.is_game_over():
                game_over = True

        screen.fill(CANVAS_COLOR)
        restart_rect = header_renderer.draw(screen, game.score, best_score)
        board_renderer.draw_frame(screen, animator.get_render_tiles(), top_left=BOARD_OFFSET)

        pygame.display.flip()

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