# SPDX-License-Identifier: Apache-2.0
# Stratified calibration addendum for the v2.0.0 discrimination phase.
#
# POST-HOC (non-preregistered) analysis. This script reads only the
# committed raw records (results/raw/v2/run-001..240.json), the frozen
# problem set (problems-v2.json), and the committed oracle
# (oracle-v2.json); it makes no judge calls. It reuses the
# sealed-criterion code in experiments/judge-enumeration-v2/analyze_v2.py
# and computes per-stratum confidence statistics, pass-to-pass drift,
# and the probability quantization histogram. Rates, means, variances,
# and the Welch contrast are computed with exact Fraction arithmetic;
# entropy and Pearson correlations require log2/sqrt and are computed
# in float. Conversion to float happens only at output time.
#
# Run with:
#     python3 scripts/stratified-calibration.py

import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict
from fractions import Fraction

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys_path = REPO_ROOT / "experiments" / "judge-enumeration-v2"
OUTPUT = REPO_ROOT / "experiments" / "judge-enumeration-v2" / "calibration.json"

import sys  # noqa: E402

sys.path.insert(0, str(sys_path))
import analyze_v2 as a  # noqa: E402

STRATA = ("S1", "S2", "S3")
N_PER_STRATUM = 80  # 40 problems x 2 passes


def mean_frac(values):
    return sum(values, Fraction(0)) / len(values)


def sd_float(values):
    """Sample standard deviation in float (sqrt is irrational)."""
    return statistics.stdev([float(v) for v in values])


def welch_contrast(g1, g2):
    """Welch two-sample t statistic on Fraction samples; float at output."""
    n1, n2 = len(g1), len(g2)
    m1, m2 = mean_frac(g1), mean_frac(g2)
    v1 = sum((x - m1) ** 2 for x in g1) / (n1 - 1)
    v2 = sum((x - m2) ** 2 for x in g2) / (n2 - 1)
    se = ((v1 / n1 + v2 / n2)) ** Fraction(1, 2)
    return {
        "mean_1": float(m1),
        "mean_2": float(m2),
        "sd_1": sd_float(g1),
        "sd_2": sd_float(g2),
        "difference": float(m1 - m2),
        "se": float(se),
        "t": float((m1 - m2) / se),
        "n_1": n1,
        "n_2": n2,
    }


def pearson(xs, ys):
    """Pearson r in float."""
    n = len(xs)
    fx = [float(x) for x in xs]
    fy = [float(y) for y in ys]
    mx, my = sum(fx) / n, sum(fy) / n
    sx = sum((x - mx) ** 2 for x in fx)
    sy = sum((y - my) ** 2 for y in fy)
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(fx, fy)) / math.sqrt(sx * sy)


def entropy_bits(probs):
    """Shannon entropy of the option-probability table in bits (float:
    log2 is irrational)."""
    return -sum(
        float(p) * math.log2(float(p)) for p in probs.values() if p > 0
    )


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]
    assert len(records) == 240

    # Enrich each record with the stated confidence, runner-up
    # probability, entropy, decoy mass, and relative gap.
    enriched = []
    for call, r in zip(calls, records):
        sel = call["response"]["answers"]["selection"]
        entry = oracle[r["problem_id"]]
        probs = r["probabilities"]
        non_selected = [p for k, p in probs.items() if k != r["selected_id"]]
        enriched.append(
            {
                **r,
                "stated_confidence": Fraction(str(sel["confidence"])),
                "runner_up_prob": max(non_selected),
                "entropy_bits": entropy_bits(probs),
                "decoy_prob": probs[entry["decoy_id"]],
                "relative_gap": Fraction(entry["delta_k"], entry["delta_z_star"]),
            }
        )

    # Per-stratum and pooled statistics.
    strata_stats = {}
    for s in STRATA:
        sub = [r for r in enriched if r["stratum"] == s]
        assert len(sub) == N_PER_STRATUM
        strata_stats[s] = {
            "n": len(sub),
            "selected_prob": {
                "mean": float(mean_frac([r["selected_prob"] for r in sub])),
                "sd": sd_float([r["selected_prob"] for r in sub]),
                "min": float(min(r["selected_prob"] for r in sub)),
                "max": float(max(r["selected_prob"] for r in sub)),
            },
            "stated_confidence": {
                "mean": float(mean_frac([r["stated_confidence"] for r in sub])),
                "sd": sd_float([r["stated_confidence"] for r in sub]),
            },
            "runner_up_prob": {
                "mean": float(mean_frac([r["runner_up_prob"] for r in sub])),
                "max": float(max(r["runner_up_prob"] for r in sub)),
            },
            "entropy_bits": {
                "mean": statistics.mean([r["entropy_bits"] for r in sub]),
            },
            "decoy_prob": {
                "mean": float(mean_frac([r["decoy_prob"] for r in sub])),
                "max": float(max(r["decoy_prob"] for r in sub)),
            },
        }

    pooled = {
        "n": len(enriched),
        "selected_prob": {
            "mean": float(mean_frac([r["selected_prob"] for r in enriched])),
            "sd": sd_float([r["selected_prob"] for r in enriched]),
        },
        "stated_confidence": {
            "mean": float(mean_frac([r["stated_confidence"] for r in enriched])),
            "sd": sd_float([r["stated_confidence"] for r in enriched]),
        },
        "runner_up_prob": {
            "mean": float(mean_frac([r["runner_up_prob"] for r in enriched])),
            "max": float(max(r["runner_up_prob"] for r in enriched)),
        },
        "entropy_bits": {
            "mean": statistics.mean([r["entropy_bits"] for r in enriched]),
        },
        "decoy_prob": {
            "mean": float(mean_frac([r["decoy_prob"] for r in enriched])),
            "max": float(max(r["decoy_prob"] for r in enriched)),
        },
    }

    # S1 vs S3 Welch contrasts (stratum-level gradient).
    s1 = [r for r in enriched if r["stratum"] == "S1"]
    s3 = [r for r in enriched if r["stratum"] == "S3"]
    contrasts = {
        "selected_prob_S1_vs_S3": welch_contrast(
            [r["selected_prob"] for r in s1], [r["selected_prob"] for r in s3]
        ),
        "stated_confidence_S1_vs_S3": welch_contrast(
            [r["stated_confidence"] for r in s1],
            [r["stated_confidence"] for r in s3],
        ),
    }

    # Gap-confidence correlation: within stratum (instance-level) and
    # pooled (stratum means drive it).
    correlations = {
        "within_stratum_r_relative_gap_vs_selected_prob": {
            s: pearson(
                [r["relative_gap"] for r in enriched if r["stratum"] == s],
                [r["selected_prob"] for r in enriched if r["stratum"] == s],
            )
            for s in STRATA
        },
        "pooled_r_relative_gap_vs_selected_prob": pearson(
            [r["relative_gap"] for r in enriched],
            [r["selected_prob"] for r in enriched],
        ),
    }

    # Pass-to-pass drift per problem: selections identical everywhere
    # (sealed result), probabilities are not.
    by_problem = defaultdict(list)
    for r in enriched:
        by_problem[r["problem_id"]].append(r)
    assert all(len(rs) == 2 for rs in by_problem.values())
    drifts = []
    argmax_changes = 0
    for pid, rs in by_problem.items():
        p1, p2 = rs[0]["probabilities"], rs[1]["probabilities"]
        assert set(p1) == set(p2)
        if max(p1, key=p1.get) != max(p2, key=p2.get):
            argmax_changes += 1
        drifts.append(abs(rs[0]["selected_prob"] - rs[1]["selected_prob"]))
    exact_same = sum(1 for d in drifts if d == 0)
    drift_stats = {
        "n_problems": len(drifts),
        "mean_abs_delta_selected_prob": float(mean_frac(drifts)),
        "max_abs_delta_selected_prob": float(max(drifts)),
        "problems_with_identical_selected_prob": exact_same,
        "fraction_identical": float(Fraction(exact_same, len(drifts))),
        "problems_with_argmax_change": argmax_changes,
    }

    # Quantization histogram: distinct probability values across all
    # 240 calls x 5 options.
    hist = Counter()
    for r in enriched:
        for p in r["probabilities"].values():
            # Group by the exact Fraction value; float is used only at
            # output time, avoiding float-key grouping precision issues.
            hist[p] += 1
    quantization = {
        "distinct_values": len(hist),
        "step": 0.01,
        "histogram": {f"{float(v):.2f}": hist[v] for v in sorted(hist)},
    }

    output = {
        "status": "post-hoc exploratory addendum; not preregistered; "
        "no preregistered endpoint is changed",
        "derivation": "results/raw/v2/run-001..240.json + problems-v2.json "
        "+ oracle-v2.json via analyze_v2.per_call_record; no judge calls",
        "strata": strata_stats,
        "pooled": pooled,
        "contrasts_S1_vs_S3": contrasts,
        "correlations_relative_gap_vs_selected_prob": correlations,
        "drift": drift_stats,
        "quantization": quantization,
    }

    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")
    print("calibration written to", OUTPUT.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
