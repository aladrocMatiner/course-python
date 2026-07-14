"""Reference search implementations for Appendix B."""

from collections import deque
from collections.abc import Hashable, Mapping, Sequence
from typing import TypeVar


Node = TypeVar("Node", bound=Hashable)
Value = TypeVar("Value")


def linear_search(values: Sequence[Value], target: Value) -> int:
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def binary_search(sorted_values: Sequence[Value], target: Value) -> int:
    left, right = 0, len(sorted_values) - 1
    while left <= right:
        middle = (left + right) // 2
        value = sorted_values[middle]
        if value == target:
            return middle
        if value < target:  # type: ignore[operator]
            left = middle + 1
        else:
            right = middle - 1
    return -1


def bfs(graph: Mapping[Node, Sequence[Node]], start: Node, target: Node) -> bool:
    if start not in graph or target not in graph:
        return False
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        for neighbor in graph.get(node, ()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False
