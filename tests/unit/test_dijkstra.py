"""Unit tests for the directed Dijkstra implementation."""

import pytest

from app.algorithms.dijkstra import dijkstra_shortest_path


def test_dijkstra_basic_path():
    """Finds the cheapest multi-hop path over a more expensive direct edge."""
    edges = [
        ("A", "B", 1),
        ("B", "C", 2),
        ("A", "C", 10),
    ]
    result = dijkstra_shortest_path(edges, "A", "C")
    assert result is not None
    assert result.path == ["A", "B", "C"]
    assert result.total_weight == 3


def test_dijkstra_directed_edges_matter():
    """Ensures directionality is enforced; reverse edge is not assumed."""
    edges = [("A", "B", 5)]
    assert dijkstra_shortest_path(edges, "B", "A") is None


def test_dijkstra_unreachable():
    """Returns None when the target node cannot be reached."""
    edges = [("A", "B", 1), ("C", "D", 2)]
    assert dijkstra_shortest_path(edges, "A", "D") is None


def test_dijkstra_rejects_non_positive_weights():
    """Validates Dijkstra precondition for positive weights."""
    with pytest.raises(ValueError):
        dijkstra_shortest_path([("A", "B", 0)], "A", "B")
