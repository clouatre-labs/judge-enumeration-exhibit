"""Exact LP vertex enumeration for the blending problem (stdlib only).

Method: every candidate vertex is the intersection of three of the
seven constraint planes; each candidate system is solved exactly over
rationals. Singular systems (parallel or dependent planes) are
discarded as non-intersecting. Remaining intersections are filtered by
feasibility (all constraints satisfied, all coordinates non-negative),
deduplicated, and the objective is maximized over the feasible
vertices. This is a sealed exhibit: the feasible vertices are frozen
into frozen_state.json and offered to the judge as pre-enumerated
candidates.

Usage:
    python3 enumerate.py                # print the optimum
    python3 enumerate.py --emit-state   # print frozen state JSON
"""

import argparse
import json
import sys
from fractions import Fraction
from itertools import combinations

from solve3x3 import solve3x3

# Constraints of the form a . x <= b over x = (x1, x2, x3).
# The blending (teneur) requirement
#   -3/10 x1 + 3/50 x2 + 3/5 x3 >= 0
# is stored in <= form by negating every coefficient.
CONSTRAINTS = [
    # name, coefficients, bound
    ("capacity_x1", (Fraction(1), Fraction(0), Fraction(0)), Fraction(25)),
    ("capacity_x2", (Fraction(0), Fraction(1), Fraction(0)), Fraction(6)),
    ("capacity_x3", (Fraction(0), Fraction(0), Fraction(1)), Fraction(4)),
    (
        "blending",
        (Fraction(3, 10), Fraction(-3, 50), Fraction(-3, 5)),
        Fraction(0),
    ),
    ("nonneg_x1", (Fraction(-1), Fraction(0), Fraction(0)), Fraction(0)),
    ("nonneg_x2", (Fraction(0), Fraction(-1), Fraction(0)), Fraction(0)),
    ("nonneg_x3", (Fraction(0), Fraction(0), Fraction(-1)), Fraction(0)),
]

OBJECTIVE = (Fraction(900), Fraction(700), Fraction(500))


def feasible(x):
    """Return True if x satisfies every constraint and x >= 0."""
    for _, coeffs, bound in CONSTRAINTS:
        lhs = sum(c * v for c, v in zip(coeffs, x))
        if lhs > bound:
            return False
    return all(v >= 0 for v in x)


def enumerate_vertices():
    """Enumerate all distinct feasible vertices exactly.

    Returns:
        (vertices, n_singular) where vertices is a list of
        (x_tuple, objective) sorted ascending by (x1, x2, x3), and
        n_singular counts constraint triples whose intersection is
        singular (no unique solution).
    """
    n_singular = 0
    points = set()
    for triple in combinations(range(len(CONSTRAINTS)), 3):
        a = [list(CONSTRAINTS[i][1]) for i in triple]
        b = [CONSTRAINTS[i][2] for i in triple]
        x = solve3x3(a, b)
        if x is None:
            n_singular += 1
            continue
        if feasible(x):
            obj = sum(c * v for c, v in zip(OBJECTIVE, x))
            points.add((tuple(x), obj))
    vertices = sorted(points, key=lambda p: (p[0][0], p[0][1], p[0][2]))
    return vertices, n_singular


def main():
    parser = argparse.ArgumentParser(
        description="Exact vertex enumeration for the blending LP."
    )
    parser.add_argument(
        "--emit-state",
        action="store_true",
        help="print the frozen state JSON (all feasible vertices sorted ascending)",
    )
    args = parser.parse_args()

    vertices, n_singular = enumerate_vertices()
    best_x, best_obj = max(vertices, key=lambda p: p[1])

    if args.emit_state:
        ids = "ABCDEFGH"
        candidates = [
            {
                "id": ids[i],
                "x": [float(v) for v in x],
                "objective": int(obj) if obj.denominator == 1 else str(obj),
            }
            for i, (x, obj) in enumerate(vertices)
        ]
        state = {
            "problem": "blending problem max 900x1+700x2+500x3",
            "candidates": candidates,
            "n_candidates": len(candidates),
        }
        json.dump(state, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(
            "optimum x* = (%s, %s, %s) M* = %s"
            % (
                best_x[0],
                best_x[1],
                best_x[2],
                best_obj,
            )
        )
        print("singular triples discarded: %d" % n_singular)


if __name__ == "__main__":
    main()
