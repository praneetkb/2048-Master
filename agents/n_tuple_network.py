# This file implements the N-tuple network value function for the RL agent.
# It maps a 4x4 board to a value by summing lookup-table entries selected by
# 17 four-cell tuples (rows, columns, 2x2 squares) across all 8 board symmetries.
# Team member responsible: João

from pathlib import Path
from typing import Any, Iterable, Optional, Sequence, Tuple, Union

import numpy as np


BOARD_SIZE = 4
BASE = 16
TUPLE_LENGTH = 4
TABLE_SIZE = BASE**TUPLE_LENGTH
FORMAT_VERSION = 1

Coordinate = Tuple[int, int]
TuplePattern = Tuple[Coordinate, ...]
PathLike = Union[str, "Path"]


def _default_tuples() -> Tuple[TuplePattern, ...]:
    rows = [tuple((row, col) for col in range(BOARD_SIZE)) for row in range(BOARD_SIZE)]
    columns = [tuple((row, col) for row in range(BOARD_SIZE)) for col in range(BOARD_SIZE)]
    squares = [
        tuple((row + dr, col + dc) for dr in range(2) for dc in range(2))
        for row in range(BOARD_SIZE - 1)
        for col in range(BOARD_SIZE - 1)
    ]
    return tuple(rows + columns + squares)


DEFAULT_TUPLES = _default_tuples()


class NTupleNetwork:
    """N-tuple value function for a 4x4 2048 grid.

    Each four-cell tuple owns one base-16 lookup table. A board value is the
    sum of the entries selected by every tuple across all eight rotations and
    reflections of the board.
    """

    def __init__(
        self,
        tuples: Optional[Iterable[Sequence[Coordinate]]] = None,
        dtype: Any = np.float32,
    ) -> None:
        self.tuples = self._normalize_tuples(DEFAULT_TUPLES if tuples is None else tuples)

        table_dtype = np.dtype(dtype)
        if not np.issubdtype(table_dtype, np.floating):
            raise TypeError("dtype must be a floating-point numpy dtype")

        self.tables = np.zeros((len(self.tuples), TABLE_SIZE), dtype=table_dtype)
        self._tuple_cells = np.asarray(
            [[row * BOARD_SIZE + col for row, col in pattern] for pattern in self.tuples],
            dtype=np.intp,
        )
        self._place_values = np.asarray([BASE**position for position in range(TUPLE_LENGTH)], dtype=np.int64)

    @staticmethod
    def _normalize_tuples(tuples: Iterable[Sequence[Coordinate]]) -> Tuple[TuplePattern, ...]:
        normalized = []
        for pattern in tuples:
            cells = []
            for coordinate in pattern:
                if len(coordinate) != 2:
                    raise ValueError("each tuple coordinate must contain (row, col)")
                row, col = coordinate
                if not isinstance(row, (int, np.integer)) or not isinstance(col, (int, np.integer)):
                    raise TypeError("tuple coordinates must be integers")
                row, col = int(row), int(col)
                if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                    raise ValueError("tuple coordinates must be inside the 4x4 board")
                cells.append((row, col))

            if len(cells) != TUPLE_LENGTH:
                raise ValueError("each tuple must contain exactly four cells")
            if len(set(cells)) != TUPLE_LENGTH:
                raise ValueError("a tuple cannot contain the same cell more than once")
            normalized.append(tuple(cells))

        if not normalized:
            raise ValueError("at least one tuple is required")
        if len(set(normalized)) != len(normalized):
            raise ValueError("duplicate tuples are not allowed")
        return tuple(normalized)

    @staticmethod
    def _tile_ranks(values: np.ndarray) -> np.ndarray:
        array = np.asarray(values)
        if not np.issubdtype(array.dtype, np.integer) or np.issubdtype(array.dtype, np.bool_):
            raise TypeError("tile values must be integers")
        if np.any(array < 0):
            raise ValueError("tile values cannot be negative")

        positive = array[array > 0]
        if positive.size and np.any((positive & (positive - 1)) != 0):
            raise ValueError("non-empty tiles must be powers of two")
        if positive.size and np.any(positive > 32768):
            raise ValueError("base-16 indexing supports tile values only up to 32768")

        ranks = np.zeros(array.shape, dtype=np.uint8)
        mask = array > 0
        if np.any(mask):
            ranks[mask] = np.log2(array[mask]).astype(np.uint8)
        return ranks

    @classmethod
    def encode(cls, tile_values: Sequence[int]) -> int:
        """Encode four tile values as little-endian base-16 digits."""
        values = np.asarray(tile_values)
        if values.shape != (TUPLE_LENGTH,):
            raise ValueError("encode expects exactly four tile values")
        ranks = cls._tile_ranks(values).astype(np.int64, copy=False)
        place_values = np.asarray([BASE**position for position in range(TUPLE_LENGTH)], dtype=np.int64)
        return int(ranks @ place_values)

    @staticmethod
    def symmetries(grid: np.ndarray) -> Tuple[np.ndarray, ...]:
        """Return four rotations and the four rotations of a reflection."""
        board = np.asarray(grid)
        if board.shape != (BOARD_SIZE, BOARD_SIZE):
            raise ValueError("grid must have shape (4, 4)")
        NTupleNetwork._tile_ranks(board)

        reflected = np.fliplr(board)
        return tuple(
            np.array(transformed, copy=True)
            for source in (board, reflected)
            for transformed in (np.rot90(source, 0), np.rot90(source, 1), np.rot90(source, 2), np.rot90(source, 3))
        )

    def feature_indices(self, grid: np.ndarray) -> np.ndarray:
        """Return the table index selected by each symmetry and tuple."""
        board = np.asarray(grid)
        if board.shape != (BOARD_SIZE, BOARD_SIZE):
            raise ValueError("grid must have shape (4, 4)")
        ranks = self._tile_ranks(board)

        reflected = np.fliplr(ranks)
        transformed_boards = [
            transformed
            for source in (ranks, reflected)
            for transformed in (np.rot90(source, 0), np.rot90(source, 1), np.rot90(source, 2), np.rot90(source, 3))
        ]

        indices = np.empty((8, len(self.tuples)), dtype=np.int64)
        for symmetry_index, transformed in enumerate(transformed_boards):
            tuple_ranks = transformed.reshape(-1)[self._tuple_cells]
            indices[symmetry_index] = tuple_ranks @ self._place_values
        return indices

    def value(self, grid: np.ndarray) -> float:
        indices = self.feature_indices(grid)
        table_numbers = np.arange(len(self.tuples), dtype=np.intp)[None, :]
        return float(self.tables[table_numbers, indices].sum(dtype=np.float64))

    def update(self, grid: np.ndarray, delta: float) -> None:
        """Distribute delta evenly over every table lookup used by value()."""
        try:
            numeric_delta = float(delta)
        except (TypeError, ValueError) as error:
            raise TypeError("delta must be a finite real number") from error
        if not np.isfinite(numeric_delta):
            raise ValueError("delta must be finite")

        indices = self.feature_indices(grid)
        amount_per_lookup = numeric_delta / indices.size
        for table_number in range(len(self.tuples)):
            np.add.at(self.tables[table_number], indices[:, table_number], amount_per_lookup)

    def save(self, path: PathLike) -> None:
        """Save tuple definitions and lookup tables without changing the path."""
        checkpoint = Path(path)
        with checkpoint.open("wb") as file:
            np.savez_compressed(
                file,
                format_version=np.asarray(FORMAT_VERSION, dtype=np.uint16),
                tuples=np.asarray(self.tuples, dtype=np.int8),
                tables=self.tables,
            )

    @classmethod
    def load(cls, path: PathLike) -> "NTupleNetwork":
        checkpoint = Path(path)
        with np.load(checkpoint, allow_pickle=False) as saved:
            required = {"format_version", "tuples", "tables"}
            if not required.issubset(saved.files):
                raise ValueError("invalid n-tuple checkpoint: required arrays are missing")

            version = int(np.asarray(saved["format_version"]).item())
            if version != FORMAT_VERSION:
                raise ValueError(f"unsupported n-tuple checkpoint version: {version}")

            tuple_array = np.asarray(saved["tuples"])
            tables = np.asarray(saved["tables"])

        if tuple_array.ndim != 3 or tuple_array.shape[1:] != (TUPLE_LENGTH, 2):
            raise ValueError("invalid n-tuple checkpoint: malformed tuple definitions")
        if tables.shape != (tuple_array.shape[0], TABLE_SIZE):
            raise ValueError("invalid n-tuple checkpoint: malformed lookup tables")
        if not np.issubdtype(tables.dtype, np.floating):
            raise ValueError("invalid n-tuple checkpoint: lookup tables must be floating point")

        tuples = [tuple((int(row), int(col)) for row, col in pattern) for pattern in tuple_array]
        network = cls(tuples=tuples, dtype=tables.dtype)
        network.tables[...] = tables
        return network
