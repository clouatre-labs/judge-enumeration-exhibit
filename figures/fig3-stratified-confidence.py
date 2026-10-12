# SPDX-License-Identifier: Apache-2.0
# POST-HOC (non-preregistered) figure: per-stratum mean selected-option
# probability and stated confidence, v2.0.0 discrimination phase. The
# preregistered endpoints are saturated at 1.000 and are reported in
# tables; this figure shows the graded confidence gradient across
# strata that the raw records contain even though selections never
# flip. Derives only from the raw v2 run records plus the committed
# oracle, reusing the sealed-criterion code in
# experiments/judge-enumeration-v2/analyze_v2.py. Labeled exploratory
# per preregistration section (e). Render with:
#     uv run --with matplotlib python figures/fig3-stratified-confidence.py

import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

STRATUM_COLORS = {"S1": "#1f77b4", "S2": "#ff7f0e", "S3": "#2ca02c"}
STRATA = ("S1", "S2", "S3")
LABELS = {
    "S1": "S1\n(gap >= 20%)",
    "S2": "S2\n(5% <= gap < 20%)",
    "S3": "S3\n(0.5% <= gap < 5%)",
}


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]
    from fractions import Fraction

    means = {s: [] for s in STRATA}
    confs = {s: [] for s in STRATA}
    for call, r in zip(calls, records):
        stated = Fraction(str(call["response"]["answers"]["selection"]["confidence"]))
        means[r["stratum"]].append(r["selected_prob"])
        confs[r["stratum"]].append(stated)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    width = 0.35
    xs = range(len(STRATA))
    for i, (vals, label) in enumerate(
        ((means, "Selected-option probability"), (confs, "Stated confidence"))
    ):
        for j, s in enumerate(STRATA):
            m = float(sum(vals[s]) / len(vals[s]))
            var = sum((float(v) - m) ** 2 for v in vals[s]) / (len(vals[s]) - 1)
            sd = var**0.5
            pos = j + (i - 0.5) * width
            ax.bar(pos, m, width * 0.92, yerr=sd, capsize=4,
                   color=STRATUM_COLORS[s], alpha=0.55 if i else 1.0,
                   error_kw={"linewidth": 1})
            ax.annotate(f"{m:.3f}", (pos, m), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=8)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([LABELS[s] for s in STRATA])
    ax.set_ylim(0.5, 1.0)
    ax.set_ylabel("Mean probability per call (error bars: sd)")
    ax.set_title("Confidence by stratum, all 240 calls (exploratory)")
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    handles = [
        Patch(facecolor="#7f7f7f", label="Selected-option probability"),
        Patch(facecolor="#7f7f7f", alpha=0.55, label="Stated confidence"),
        Line2D([0], [0], color="#7f7f7f", linewidth=1, label="sd within stratum"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig3-stratified-confidence.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
