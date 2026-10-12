# SPDX-License-Identifier: Apache-2.0
# EXPLORATORY figure: pass-1 vs pass-2 selected-option probability per
# problem, v2.0.0 discrimination phase. The preregistered stability
# endpoint (per-problem disagreement) is saturated at 0/120 and is
# reported in tables; this figure shows how closely the two calls track
# each other in confidence. Derives only from the raw v2 run records
# plus the committed oracle, reusing the sealed-criterion code in
# experiments/judge-enumeration-v2/analyze_v2.py. Labeled exploratory
# per preregistration section (e). Render with:
#     uv run --with matplotlib python figures/fig3-pass1-vs-pass2.py

import pathlib
import sys
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

POINT_COLOR = "#1f77b4"
DIAGONAL_COLOR = "#7f7f7f"


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]

    by_problem = {}
    for r in records:
        by_problem.setdefault(r["problem_id"], {})[r["pass"]] = r["selected_prob"]

    xs = [float(by_problem[pid][1]) for pid in sorted(by_problem)]
    ys = [float(by_problem[pid][2]) for pid in sorted(by_problem)]
    diffs = [abs(x - y) for x, y in zip(xs, ys)]
    max_diff = max(diffs)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.plot([0.5, 1.0], [0.5, 1.0], color=DIAGONAL_COLOR, linestyle="--",
            linewidth=1, label="Identical confidence")
    ax.scatter(xs, ys, s=26, alpha=0.75, color=POINT_COLOR)
    ax.set_xlim(0.5, 1.02)
    ax.set_ylim(0.5, 1.02)
    ax.set_xlabel("Pass-1 selected-option probability")
    ax.set_ylabel("Pass-2 selected-option probability")
    ax.set_title("Per-problem confidence across passes (exploratory)")
    ax.text(0.03, 0.95, f"selections agree: 120/120\nmax |p1 - p2| = {max_diff:.2f}",
            transform=ax.transAxes, fontsize=10, verticalalignment="top")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig3-pass1-vs-pass2.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
