# This file is responsible for running pygame window, calling agents, updating game state and controlling speed
# Team member responsible: Jayden

import pygame

from agents.expectimax_rl_agent import ExpectimaxAgent
from agents.random_agent import RandomAgent
from game.game import Game
from ui.menu import run_menu
from ui.renderer import BoardRenderer, ComparisonRenderer, HeaderRenderer
from ui.animation import TileAnimator
from ui.comparison import compare_agents
from ui.theme import CANVAS, INK, INK_SOFT, blit_center, font
from training.checkpoints import load_value_function

POST_MOVE_PAUSE_MS = 0

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

AGENT_LABELS = {
    "random": "Random",
    "expectimax": "Expectimax",
    "expectimaxRL": "Expectimax + RL",
}


def get_agent(choice):
    if choice == "random":
        return RandomAgent()
    if choice == "expectimax":
        # Heuristic baseline: no network, so evaluate() uses 100*empty + max_tile.
        return ExpectimaxAgent(depth=2)
    if choice == "expectimaxRL":
        # Same search, but the leaves are scored by the trained value function.
        return ExpectimaxAgent(depth=2, network=load_value_function())


def run_comparison(screen):
    renderer = ComparisonRenderer()
    clock = pygame.time.Clock()

    renderer.draw(screen, {}, running=True)
    pygame.display.flip()

    results = compare_agents()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True

        renderer.draw(screen, results)
        pygame.display.flip()


def run_game_loop(screen, agent, agent_label=None):
    game = Game()
    board_renderer = BoardRenderer()
    header_renderer = HeaderRenderer(agent_label=agent_label)
    animator = TileAnimator()
    animator.snapshot(game.board.grid)
    best_score = 0

    board_left = (screen.get_width() - board_renderer.pixel_size) // 2
    board_top = HeaderRenderer.HEIGHT + 34
    board_offset = (board_left, board_top)

    clock = pygame.time.Clock()
    idle_time = 0

    game_over = False
    restart_rect = pygame.Rect(0, 0, 0, 0)

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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

        screen.fill(CANVAS)
        restart_rect = header_renderer.draw(screen, game.score, best_score)
        board_renderer.draw_frame(screen, animator.get_render_tiles(), top_left=board_offset)

        if game_over:
            _draw_game_over(screen, board_renderer, board_offset, game)

        _draw_footer(screen)

        pygame.display.flip()


def _draw_game_over(screen, board_renderer, board_offset, game):
    size = board_renderer.pixel_size
    overlay = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(
        overlay, (250, 248, 245, 205), overlay.get_rect(), border_radius=16
    )
    screen.blit(overlay, board_offset)

    center_x = board_offset[0] + size // 2
    center_y = board_offset[1] + size // 2

    blit_center(
        screen,
        font(30, "bold").render("Game over", True, INK),
        (center_x, center_y - 28),
    )
    blit_center(
        screen,
        font(15, "regular").render(
            f"Final score {game.score:,}   best tile {int(game.board.grid.max()):,}",
            True,
            INK_SOFT,
        ),
        (center_x, center_y + 10),
    )
    blit_center(
        screen,
        font(13, "regular").render("Restart to play again", True, INK_SOFT),
        (center_x, center_y + 38),
    )


def _draw_footer(screen):
    hint = font(12, "regular").render("Esc for the menu", True, INK_SOFT)
    screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 24)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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

        if not run_game_loop(screen, agent, agent_label=AGENT_LABELS.get(choice)):
            break

    pygame.quit()


if __name__ == "__main__":
    main()
