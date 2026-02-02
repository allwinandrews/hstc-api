"""Shortest-path utility for directed, positively weighted graphs."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class PathResult:
    """Shortest-path output: full path plus total weight."""
    path: List[str]
    total_weight: int


def dijkstra_shortest_path(
    edges: List[Tuple[str, str, int]],
    start: str,
    target: str,
) -> PathResult | None:
    """
    Compute the shortest path in a directed, positively weighted graph.

    Args:
        edges: Directed edges as (from_node, to_node, weight).
        start: Starting node id.
        target: Target node id.

    Returns:
        PathResult with path=[start..target] and total_weight, or None if
        the target is unreachable.

    Raises:
        ValueError: If any edge has a non-positive weight (Dijkstra precondition).
    """
    # Build adjacency list to preserve directed edge weights.
    graph: Dict[str, List[Tuple[str, int]]] = {}
    for u, v, w in edges:
        if w <= 0:
            raise ValueError("Dijkstra requires all weights to be positive")
        graph.setdefault(u, []).append((v, w))

    # Min-heap: (distance_so_far, node)
    heap: List[Tuple[int, str]] = [(0, start)]
    dist: Dict[str, int] = {start: 0}
    prev: Dict[str, str] = {}

    visited = set()

    while heap:
        cur_dist, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)

        if node == target:
            break

        for neighbor, weight in graph.get(node, []):
            new_dist = cur_dist + weight
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))

    if target not in dist:
        return None

    # Reconstruct path
    path = [target]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()

    return PathResult(path=path, total_weight=dist[target])
