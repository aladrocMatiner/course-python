import unittest

from search_contract import bfs


class SearchContractTests(unittest.TestCase):
    def test_bfs_reachable_and_disconnected(self) -> None:
        graph = {"A": ["B"], "B": [], "C": []}
        self.assertTrue(bfs(graph, "A", "B"))
        self.assertFalse(bfs(graph, "A", "C"))

    def test_bfs_requires_hashable_neighbor_nodes(self) -> None:
        graph = {"A": [["B"]], "B": []}
        with self.assertRaises(TypeError):
            bfs(graph, "A", "B")


if __name__ == "__main__":
    unittest.main()
