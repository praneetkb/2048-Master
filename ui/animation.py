BOARD_SIZE = 4

SLIDE_DURATION_MS = 120
MERGE_POP_DURATION_MS = 110
SPAWN_DURATION_MS = 150

def _lines_for(direction):
    lines = []

    if direction in ("left", "right"):
        for r in range(BOARD_SIZE):
            if direction == "left":
                cols = range(BOARD_SIZE)
            else:
                cols = range(BOARD_SIZE - 1, -1, -1)
            lines.append([(r, c) for c in cols])
    elif direction in ("up", "down"):
        for c in range(BOARD_SIZE):
            if direction == "up":
                rows = range(BOARD_SIZE)
            else:
                rows = range(BOARD_SIZE - 1, -1, -1)
            lines.append([(r, c) for r in rows])
    else:
        raise ValueError(f"Unknown direction: {direction}")

    return lines

def _trace_line(coords, grid):
    tiles = [(k, int(grid[r][c])) for k, (r, c) in enumerate(coords) if grid[r][c] != 0]

    events = []
    dest = 0
    i = 0

    while i < len(tiles):
        src_k, value = tiles[i]

        if i + 1 < len(tiles) and tiles[i + 1][1] == value:
            src_k2, _ = tiles[i + 1]
            dest_coord = coords[dest]
            events.append({"from": coords[src_k], "to": dest_coord, "value": value, "merge": True})
            events.append({"from": coords[src_k2], "to": dest_coord, "value": value, "merge": True})
            i += 2
        else:
            dest_coord = coords[dest]
            events.append({"from": coords[src_k], "to": dest_coord, "value": value, "merge": False})
            i += 1

        dest += 1

    return events

def trace_move(grid, direction):
    result_grid = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    events = []

    for coords in _lines_for(direction):
        for event in _trace_line(coords, grid):
            events.append(event)
            r, c = event["to"]
            if event["merge"]:
                result_grid[r][c] = event["value"] * 2
            else:
                result_grid[r][c] = event["value"]

    return result_grid, events


def _ease_out(t):
    return 1 - (1 - t) ** 2


def _pop_scale(elapsed, duration):
    if duration <= 0:
        return 1.0
    t = min(1.0, elapsed / duration)
    return 0.5 + 0.5 * _ease_out(t)


class TileAnimator:

    def __init__(
        self,
        slide_duration=SLIDE_DURATION_MS,
        merge_pop_duration=MERGE_POP_DURATION_MS,
        spawn_duration=SPAWN_DURATION_MS,
    ):
        self.slide_duration = slide_duration
        self.merge_pop_duration = merge_pop_duration
        self.spawn_duration = spawn_duration

        self._motions = []
        self._merged_cells = []
        self._spawn_cell = None
        self._elapsed = 0
        self._grid = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def snapshot(self, grid):
        self._grid = [[int(v) for v in row] for row in grid]
        self._motions = []
        self._merged_cells = []
        self._spawn_cell = None
        self._elapsed = 0

    def start_move(self, old_grid, direction, new_grid):
        result_grid, events = trace_move(old_grid, direction)

        self._motions = events
        self._merged_cells = list({event["to"] for event in events if event["merge"]})
        self._spawn_cell = self._find_spawned_cell(result_grid, new_grid)
        self._elapsed = 0
        self._grid = [[int(v) for v in row] for row in new_grid]

    @staticmethod
    def _find_spawned_cell(result_grid, new_grid):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if result_grid[r][c] == 0 and int(new_grid[r][c]) != 0:
                    return (r, c, int(new_grid[r][c]))
        return None

    def update(self, dt_ms):
        self._elapsed += dt_ms

    def is_animating(self):
        has_motion = bool(self._motions) or self._spawn_cell is not None
        return has_motion and self._elapsed < self._total_duration()

    def _total_duration(self):
        return self.slide_duration + max(self.merge_pop_duration, self.spawn_duration)

    def get_render_tiles(self):
        if not self._motions and self._spawn_cell is None:
            return self._resting_tiles()

        if self.slide_duration:
            slide_t = min(1.0, self._elapsed / self.slide_duration)
        else:
            slide_t = 1.0
        eased = _ease_out(slide_t)
        landed = slide_t >= 1.0

        tiles = []

        for event in self._motions:
            if event["merge"] and landed:
                continue
            from_r, from_c = event["from"]
            to_r, to_c = event["to"]
            row = from_r + (to_r - from_r) * eased
            col = from_c + (to_c - from_c) * eased
            tiles.append({"row": row, "col": col, "value": event["value"], "scale": 1.0})

        if landed:
            pop_elapsed = self._elapsed - self.slide_duration

            for (r, c) in self._merged_cells:
                scale = _pop_scale(pop_elapsed, self.merge_pop_duration)
                tiles.append({"row": r, "col": c, "value": self._grid[r][c], "scale": scale})

            if self._spawn_cell is not None:
                r, c, value = self._spawn_cell
                scale = _pop_scale(pop_elapsed, self.spawn_duration)
                tiles.append({"row": r, "col": c, "value": value, "scale": scale})

        return tiles

    def _resting_tiles(self):
        tiles = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                value = self._grid[r][c]
                if value:
                    tiles.append({"row": r, "col": c, "value": value, "scale": 1.0})
        return tiles