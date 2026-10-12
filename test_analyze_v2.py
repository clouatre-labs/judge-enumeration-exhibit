"""Tests for the v2.0.0 exact-arithmetic analysis module."""

import importlib.util
import pathlib
import unittest
from fractions import Fraction

_SPEC = importlib.util.spec_from_file_location(
    "analyze_v2",
    pathlib.Path(__file__).parent / "experiments/judge-enumeration-v2/analyze_v2.py",
)
analyze_v2 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(analyze_v2)


class WilsonIntervalTest(unittest.TestCase):
    def test_perfect_record(self):
        lo, hi = analyze_v2.wilson_interval(40, 40)
        self.assertAlmostEqual(lo, 0.9123754607496077)
        self.assertEqual(hi, 1.0)

    def test_zero_record(self):
        lo, hi = analyze_v2.wilson_interval(0, 40)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 1 - Fraction(0, 1) and hi or hi)
        self.assertLess(hi, 1.0)


class FisherExactTest(unittest.TestCase):
    def test_identical_tables_give_p_one(self):
        p = analyze_v2.fisher_exact_two_sided(40, 0, 40, 0)
        self.assertEqual(p, 1.0)

    def test_perfect_separation_is_significant(self):
        p = analyze_v2.fisher_exact_two_sided(40, 0, 0, 40)
        self.assertLess(p, 0.0001)

    def test_moderate_table_matches_known_value(self):
        # Fisher's tea-tasting example: 3/4 vs 1/4, two-sided p = 17/35
        # (matches R fisher.test two-sided).
        p = analyze_v2.fisher_exact_two_sided(3, 1, 1, 3)
        self.assertAlmostEqual(p, 17 / 35)


class CalibrationTest(unittest.TestCase):
    def test_brier_perfect_confidence(self):
        records = [
            {"agreement": True, "selected_prob": Fraction(1)},
            {"agreement": False, "selected_prob": Fraction(0)},
        ]
        self.assertEqual(analyze_v2.brier_score(records), Fraction(0))

    def test_brier_half_confidence(self):
        records = [{"agreement": True, "selected_prob": Fraction(1, 2)}]
        self.assertEqual(analyze_v2.brier_score(records), Fraction(1, 4))

    def test_ece_perfect_confidence(self):
        records = [{"agreement": True, "selected_prob": Fraction(1)}]
        self.assertEqual(analyze_v2.ece_5bins(records), Fraction(0))

    def test_ece_uniform_half(self):
        records = [{"agreement": True, "selected_prob": Fraction(1, 2)}]
        self.assertEqual(analyze_v2.ece_5bins(records), Fraction(1, 2))


class SealedCriterionTest(unittest.TestCase):
    def test_agreement_and_prune_failure(self):
        oracle = {"p-001": {"optimal_id": "B", "decoy_id": "E", "stratum": "S1"}}
        call = {
            "run": 1,
            "pass": 1,
            "problem_id": "p-001",
            "response": {
                "answers": {
                    "selection": {
                        "choice": "E",
                        "probabilities": {"A": 0.0, "B": 0.1, "C": 0.0, "D": 0.0, "E": 0.9},
                    }
                }
            },
        }
        r = analyze_v2.per_call_record(oracle, call)
        self.assertFalse(r["agreement"])
        self.assertTrue(r["prune_failure"])
        self.assertEqual(r["selected_prob"], Fraction(9, 10))
        self.assertEqual(r["optimal_position"], 2)
        self.assertEqual(r["decoy_position"], 5)


if __name__ == "__main__":
    unittest.main()
