"""Tests for exact LP vertex enumeration (stdlib only)."""

import unittest
from fractions import Fraction

from enumerate import CONSTRAINTS, enumerate_vertices
from solve3x3 import solve3x3


class TestSolve3x3(unittest.TestCase):
    def test_known_solution(self):
        # x + y = 2, x - y = 0, z = 3  =>  (1, 1, 3)
        x = solve3x3(
            [[1, 1, 0], [1, -1, 0], [0, 0, 1]],
            [2, 0, 3],
        )
        self.assertEqual(x, [Fraction(1), Fraction(1), Fraction(3)])

    def test_singular_returns_none(self):
        # Two parallel planes: no unique solution.
        x = solve3x3(
            [[1, 0, 0], [2, 0, 0], [0, 1, 0]],
            [1, 2, 1],
        )
        self.assertIsNone(x)


class TestEnumeration(unittest.TestCase):
    def test_exactly_ten_feasible_vertices(self):
        vertices, n_singular = enumerate_vertices()
        self.assertEqual(len(vertices), 7)
        # C(7,3) = 35 triples total; the singular ones are discarded
        # without aborting the enumeration. The remaining feasible
        # intersections deduplicate to 7 distinct vertices (the origin
        # arises from four degenerate triples).
        self.assertEqual(n_singular, 15)
        self.assertLess(len(vertices) + n_singular, 35)

    def test_singular_capacity_vs_nonneg_skipped(self):
        # capacity_x1 (index 0) and nonneg_x1 (index 4) are parallel:
        # any triple containing both must be discarded, not raise.
        coeffs = [c for _, c, _ in CONSTRAINTS]
        self.assertIsNone(
            solve3x3(
                [list(coeffs[0]), list(coeffs[4]), list(coeffs[1])],
                [Fraction(25), Fraction(0), Fraction(6)],
            )
        )

    def test_optimum(self):
        vertices, _ = enumerate_vertices()
        best_x, best_obj = max(vertices, key=lambda p: p[1])
        self.assertEqual(best_x, (Fraction(46, 5), Fraction(6), Fraction(4)))
        self.assertEqual(best_obj, Fraction(14480))


if __name__ == "__main__":
    unittest.main()
