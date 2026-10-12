# SPDX-License-Identifier: Apache-2.0
# Calibration reliability plot for the ECE bins, v2.0.0 discrimination
# phase. Recomputes the 5 equal-width bins on the selected-option
# probability exactly as experiments/judge-enumeration-v2/analyze_v2.py
# does (Fraction arithmetic), from the raw v2 run records plus the
# committed oracle. Render with:
#     uv run --with matplotlib python figures/fig2-calibration.py

import pathlib
import sys
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

BIN_COLOR = "#1f77b4"
DIAGONAL_COLOR = "#7f7f7f"


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]

    bins = [[] for _ in range(5)]
    for r in records:
        bins[min(4, int(r["selected_prob"] * 5))].append(r)
    centers, confs, accs, counts = [], [], [], []
    for i, b in enumerate(bins):
        lo, hi = i / 5, (i + 1) / 5
        if not b:
            continue
        conf = sum((r["selected_prob"] for r in b), Fraction(0)) / len(b)
        acc = Fraction(sum(1 for r in b if r["agreement"]), len(b))
        centers.append((lo + hi) / 2)
        confs.append(float(conf))
        accs.append(float(acc))
        counts.append(len(b))

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.plot([0, 1], [0, 1], color=DIAGONAL_COLOR, linestyle="--",
            linewidth=1, label="Perfect calibration")
    ax.bar(centers, accs, width=0.18, color=BIN_COLOR,
           label="Bin accuracy (all 1.0)")
    ax.scatter(confs, accs, color="#d62728", zorder=3,
               label="Mean confidence per bin")
    for cx, cy, n in zip(confs, accs, counts):
        ax.annotate(f"n={n}", (cx, cy), textcoords="offset points",
                    xytext=(6, 6), fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("Mean confidence (selected-option probability)")
    ax.set_ylabel("Accuracy")
    ax.set_title("Reliability diagram, 5 equal-width bins (ECE 0.1366)")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig2-calibration.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
