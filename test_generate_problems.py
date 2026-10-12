"""Tests for the v2.0 problem set generator (stdlib only)."""

import unittest
from fractions import Fraction

from generate_problems import (
    A_ROWS,
    B_MAX,
    COORD_MAX,
    SEED,
    build_document,
    feasible,
    objective,
    position_schedule,
    violates_upper_bounds_only,
)


class TestDeterminism(unittest.TestCase):
    def test_same_seed_same_output(self):
        doc1, oracle1 = build_document()
        doc2, oracle2 = build_document()
        self.assertEqual(doc1, doc2)
        self.assertEqual(oracle1, oracle2)


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.doc, self.oracle = build_document()

    def test_all_strata_n_40(self):
        for stratum in ("S1", "S2", "S3"):
            n = sum(
                1 for p in self.doc["problems"] if p["stratum"] == stratum
            )
            self.assertEqual(n, 40)

    def test_no_objective_values_in_judge_facing_fields(self):
        for p in self.doc["problems"]:
            self.assertNotIn("objective", p)
            for cand in p["candidates"]:
                self.assertEqual(set(cand.keys()), {"id", "x"})

    def test_menu_shape(self):
        for p in self.doc["problems"]:
            self.assertEqual(len(p["candidates"]), 5)
            ids = [c["id"] for c in p["candidates"]]
            self.assertEqual(ids, ["A", "B", "C", "D", "E"])
            for cand in p["candidates"]:
                self.assertEqual(len(cand["x"]), 3)
                self.assertTrue(
                    all(
                        isinstance(v, int) and 0 <= v <= COORD_MAX
                        for v in cand["x"]
                    )
                )

    def test_c_and_bounds_in_range(self):
        for p in self.doc["problems"]:
            self.assertTrue(all(1 <= v <= 9 for v in p["c"]))
            self.assertTrue(all(1 <= v <= B_MAX for v in p["b"][:3]))
            self.assertEqual(p["b"][3:], [0, 0, 0])
            self.assertEqual(p["A"], A_ROWS)


class TestInvariants(unittest.TestCase):
    def setUp(self):
        self.doc, self.oracle = build_document()

    def test_feasible_menu_vertices_against_stated_constraints(self):
        for p in self.doc["problems"]:
            o = self.oracle[p["problem_id"]]
            for cand in p["candidates"]:
                if cand["id"] == o["decoy_id"]:
                    continue
                self.assertTrue(
                    feasible(cand["x"], p["b"]),
                    "feasible candidate %s infeasible in %s"
                    % (cand["id"], p["problem_id"]),
                )

    def test_decoy_infeasible_via_upper_bounds_only(self):
        for p in self.doc["problems"]:
            o = self.oracle[p["problem_id"]]
            decoy = next(
                c for c in p["candidates"] if c["id"] == o["decoy_id"]
            )
            self.assertFalse(feasible(decoy["x"], p["b"]))
            self.assertTrue(violates_upper_bounds_only(decoy["x"], p["b"]))

    def test_decoy_super_optimal(self):
        for p in self.doc["problems"]:
            o = self.oracle[p["problem_id"]]
            c = p["c"]
            decoy = next(
                cand
                for cand in p["candidates"]
                if cand["id"] == o["decoy_id"]
            )
            self.assertGreater(
                objective(c, decoy["x"]),
                o["z_star"],
                "decoy not super-optimal in %s" % p["problem_id"],
            )

    def test_strict_unique_optimum_and_strata(self):
        thresholds = {
            "S1": (Fraction(1, 5), None),
            "S2": (Fraction(1, 20), Fraction(1, 5)),
            "S3": (Fraction(1, 200), Fraction(1, 20)),
        }
        for p in self.doc["problems"]:
            o = self.oracle[p["problem_id"]]
            vals = sorted(
                (v for k, v in o["objective_values"].items()
                 if k != o["decoy_id"]),
                reverse=True,
            )
            self.assertEqual(vals[0], o["z_star"])
            self.assertEqual(vals[1], o["z_second"])
            self.assertGreater(o["z_star"], o["z_second"])
            self.assertGreaterEqual(o["z_star"], 21)
            lo, hi = thresholds[p["stratum"]]
            delta = Fraction(o["delta_k"], o["delta_z_star"])
            self.assertGreaterEqual(delta, lo)
            if hi is not None:
                self.assertLess(delta, hi)
            self.assertEqual(o["delta_k"], o["z_star"] - o["z_second"])


class TestPositionBalancing(unittest.TestCase):
    def setUp(self):
        self.doc, self.oracle = build_document()

    def test_optimum_each_position_8_times_per_stratum(self):
        for stratum in ("S1", "S2", "S3"):
            counts = {i: 0 for i in range(5)}
            for p in self.doc["problems"]:
                if p["stratum"] != stratum:
                    continue
                ids = [c["id"] for c in p["candidates"]]
                counts[ids.index(self.oracle[p["problem_id"]]["optimal_id"])] += 1
            self.assertEqual(
                counts, {i: 8 for i in range(5)},
                "optimum positions unbalanced in %s" % stratum,
            )

    def test_decoy_each_position_8_times_per_stratum(self):
        for stratum in ("S1", "S2", "S3"):
            counts = {i: 0 for i in range(5)}
            for p in self.doc["problems"]:
                if p["stratum"] != stratum:
                    continue
                ids = [c["id"] for c in p["candidates"]]
                counts[ids.index(self.oracle[p["problem_id"]]["decoy_id"])] += 1
            self.assertEqual(
                counts, {i: 8 for i in range(5)},
                "decoy positions unbalanced in %s" % stratum,
            )

    def test_optimum_and_decoy_never_colocated(self):
        for p in self.doc["problems"]:
            o = self.oracle[p["problem_id"]]
            self.assertNotEqual(o["optimal_id"], o["decoy_id"])

    def test_schedule_pairs_are_disjoint(self):
        for vpos, dpos in position_schedule():
            self.assertNotEqual(vpos, dpos)


class TestPass2Order(unittest.TestCase):
    def test_pass2_permutation_of_problem_ids(self):
        doc, _ = build_document()
        ids = [p["problem_id"] for p in doc["problems"]]
        self.assertEqual(sorted(doc["pass2_order"]), sorted(ids))
        self.assertNotEqual(doc["pass2_order"], ids)

    def test_seed_committed(self):
        doc, _ = build_document()
        self.assertEqual(doc["seed"], SEED)


if __name__ == "__main__":
    unittest.main()
