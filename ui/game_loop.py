# This file is responsible for running pygame window, calling agents, updating game state and controlling speed
# Team member responsible: Jayden

import threading

import pygame

from agents.expectimax_rl_agent import ExpectimaxAgent
from agents.random_agent import RandomAgent
from game.game import Game
from training.checkpoints import load_value_function
from ui.animation import TileAnimator
from ui.comparison import compare_agents
from ui.menu import run_menu
from ui.renderer import BoardRenderer, ComparisonRenderer, HeaderRenderer
from ui.theme import CANVAS, INK, INK_SOFT, blit_center, font

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

    results = {}
    progress = {}
    lock = threading.Lock()
    done = threading.Event()

    def on_result(name, stats):
        with lock:
            results[name] = stats

    def on_progress(name, played, total):
        with lock:
            progress.clear()
            progress.update({"name": name, "played": played, "total": total})

    def work():
        try:
            compare_agents(on_result=on_result, on_progress=on_progress)
        finally:
            done.set()

    worker = threading.Thread(target=work, daemon=True)
    worker.start()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:  # noqa: SIM102
                if event.key == pygame.K_ESCAPE:
                    return True

        with lock:
            snapshot = dict(results)
            current = dict(progress)

        renderer.draw(
            screen,
            snapshot,
            running=not done.is_set(),
            progress=current if not done.is_set() else None,
        )
        pygame.display.flip()


def run_game_loop(screen, agent, agent_label=None):
    board_renderer = BoardRenderer()
    header_renderer = HeaderRenderer(agent_label=agent_label)

    board_left = (screen.get_width() - board_renderer.pixel_size) // 2
    board_top = HeaderRenderer.HEIGHT + 34
    board_offset = (board_left, board_top)

    clock = pygame.time.Clock()
    best_score = 0

    while True:
        game = Game()
        animator = TileAnimator()
        animator.snapshot(game.board.grid)

        idle_time = 0
        game_over = False
        restart = False
        restart_rect = pygame.Rect(0, 0, 0, 0)

        while not restart:
            dt = clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.MOUSEBUTTONDOWN:  # noqa: SIM102
                    if restart_rect.collidepoint(event.pos):
                        restart = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    if event.key == pygame.K_r:
                        restart = True

            if restart:
                break

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

                    if game.score > best_score:  # noqa: PLR1730
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


_overlay_cache: dict[int, pygame.Surface] = {}


def _draw_game_over(screen, board_renderer, board_offset, game):
    size = board_renderer.pixel_size

    overlay = _overlay_cache.get(size)
    if overlay is None:
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(
            overlay, (250, 248, 245, 205), overlay.get_rect(), border_radius=16
        )
        _overlay_cache[size] = overlay

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
        font(13, "regular").render("Restart, or press R, to play again", True, INK_SOFT),
        (center_x, center_y + 38),
    )


def _draw_footer(screen):
    hint = font(12, "regular").render("R to restart, Esc for the menu", True, INK_SOFT)
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
