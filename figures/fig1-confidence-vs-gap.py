# SPDX-License-Identifier: Apache-2.0
# EXPLORATORY figure: per-call selected-option probability against the
# committed relative optimality gap, v2.0.0 discrimination phase. The
# preregistered endpoints (both-call agreement) are saturated at 1.000
# and are reported in tables, not plotted; this figure shows the graded
# variation that the raw records do contain. Derives only from the raw
# v2 run records plus the committed oracle, reusing the
# sealed-criterion code in
# experiments/judge-enumeration-v2/analyze_v2.py. Labeled exploratory
# per preregistration section (e). Render with:
#     uv run --with matplotlib python figures/fig1-confidence-vs-gap.py

import pathlib
import sys
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

STRATUM_COLORS = {"S1": "#1f77b4", "S2": "#ff7f0e", "S3": "#2ca02c"}


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for stratum in ("S1", "S2", "S3"):
        xs, ys = [], []
        for r in records:
            if r["stratum"] != stratum:
                continue
            entry = oracle[r["problem_id"]]
            delta_pct = Fraction(entry["delta_k"], entry["delta_z_star"]) * 100
            xs.append(float(delta_pct))
            ys.append(float(r["selected_prob"]))
        ax.scatter(xs, ys, s=22, alpha=0.75, color=STRATUM_COLORS[stratum],
                   label=stratum)
        mean = sum(ys) / len(ys)
        ax.hlines(mean, min(xs), max(xs), color=STRATUM_COLORS[stratum],
                  linestyle=":", linewidth=1.6)
        ax.annotate(f"mean {mean:.3f}", (max(xs), mean),
                    textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=8,
                    color=STRATUM_COLORS[stratum])
    ax.set_xscale("log")
    ax.set_xlim(0.4, 60)
    ax.set_ylim(0.5, 1.02)
    ax.set_xlabel("Relative optimality gap delta = (z* - z2) / z* (%)")
    ax.set_ylabel("Selected-option probability (per call)")
    ax.set_title("Confidence vs problem difficulty, all 240 calls (exploratory)")
    ax.axhline(1.0, color="#7f7f7f", linestyle="--", linewidth=1)
    ax.set_xlim(0.3, 110)
    ax.legend(title="Stratum", loc="lower right", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig1-confidence-vs-gap.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
