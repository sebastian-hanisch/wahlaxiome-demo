"""Gemeinsame Fixtures: Mini-Profile, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import wax_algorithm as A  # noqa: E402


@pytest.fixture
def tb3():
    """Gleichstand: A vor B vor C."""
    return np.array([0, 1, 2])


def counts(m, *groups):
    """Zählvektor aus (Anzahl, Rangfolge)-Paaren, z. B. counts(3, (1, "ABC"), (2, "CAB"))."""
    _, _, index = A.ranking_tables(m)
    c = np.zeros(len(index), dtype=int)
    for n, word in groups:
        c[index[tuple("ABCD".index(ch) for ch in word)]] += n
    return c


@pytest.fixture
def make_counts():
    return counts
