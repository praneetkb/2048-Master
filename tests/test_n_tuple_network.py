import tempfile
import unittest
from pathlib import Path

import numpy as np

from agents.n_tuple_network import NTupleNetwork


ASYMMETRIC_BOARD = np.array(
    [
        [4, 8, 4, 64],
        [512, 128, 2, 256],
        [2, 16, 512, 512],
        [256, 64, 2, 1024],
    ],
    dtype=np.int64,
)


class TestNTupleNetwork(unittest.TestCase):
    def test_default_architecture_has_rows_columns_and_two_by_two_squares(self):
        network = NTupleNetwork()

        self.assertEqual(len(network.tuples), 17)
        self.assertEqual(network.tables.shape, (17, 16**4))
        self.assertEqual(network.tables.dtype, np.float32)
        self.assertTrue(np.all(network.tables == 0.0))

    def test_encode_uses_tile_exponents_as_base_16_digits(self):
        index = NTupleNetwork.encode([8, 4, 2, 2])

        self.assertEqual(index, 4387)

    def test_symmetries_returns_four_rotations_and_their_reflections(self):
        symmetries = NTupleNetwork.symmetries(ASYMMETRIC_BOARD)

        self.assertEqual(len(symmetries), 8)
        self.assertEqual(len({board.tobytes() for board in symmetries}), 8)
        np.testing.assert_array_equal(symmetries[0], ASYMMETRIC_BOARD)

    def test_update_changes_exact_entries_read_by_value(self):
        network = NTupleNetwork(tuples=[((0, 0), (0, 1), (0, 2), (0, 3))])
        indices = network.feature_indices(ASYMMETRIC_BOARD)

        self.assertEqual(len(set(indices[:, 0].tolist())), 8)

        network.update(ASYMMETRIC_BOARD, delta=8.0)

        np.testing.assert_allclose(network.tables[0, indices[:, 0]], 1.0)
        self.assertAlmostEqual(network.value(ASYMMETRIC_BOARD), 8.0, places=6)

    def test_value_is_invariant_under_all_eight_board_symmetries(self):
        network = NTupleNetwork()
        network.update(ASYMMETRIC_BOARD, delta=13.5)

        values = [network.value(board) for board in network.symmetries(ASYMMETRIC_BOARD)]

        np.testing.assert_allclose(values, values[0], rtol=0.0, atol=1e-6)

    def test_save_and_load_round_trip_preserves_model_and_exact_path(self):
        network = NTupleNetwork()
        network.update(ASYMMETRIC_BOARD, delta=7.25)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "network.checkpoint"
            network.save(path)
            loaded = NTupleNetwork.load(path)

            self.assertTrue(path.is_file())
            self.assertFalse(Path(str(path) + ".npz").exists())
            self.assertEqual(loaded.tuples, network.tuples)
            np.testing.assert_array_equal(loaded.tables, network.tables)
            self.assertEqual(loaded.value(ASYMMETRIC_BOARD), network.value(ASYMMETRIC_BOARD))

    def test_rejects_invalid_boards_and_tiles(self):
        network = NTupleNetwork()

        with self.assertRaisesRegex(ValueError, "shape"):
            network.value(np.zeros((3, 3), dtype=int))
        with self.assertRaisesRegex(ValueError, "powers of two"):
            network.value(np.array([[3] + [0] * 3] + [[0] * 4] * 3, dtype=int))
        with self.assertRaisesRegex(ValueError, "32768"):
            network.value(np.array([[65536] + [0] * 3] + [[0] * 4] * 3, dtype=int))

    def test_value_and_update_do_not_mutate_the_board(self):
        network = NTupleNetwork()
        board = ASYMMETRIC_BOARD.copy()
        original = board.copy()

        network.value(board)
        network.update(board, delta=1.0)

        np.testing.assert_array_equal(board, original)


if __name__ == "__main__":
    unittest.main()
