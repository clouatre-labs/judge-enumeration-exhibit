# SPDX-License-Identifier: Apache-2.0
# Per-stratum agreement with Wilson 95% intervals, v2.0.0 discrimination
# phase. Derives only from the raw v2 run records plus the committed
# oracle, reusing the sealed-criterion code in
# experiments/judge-enumeration-v2/analyze_v2.py so the plotted numbers
# are the endpoint numbers. Render with:
#     uv run --with matplotlib python figures/fig1-stratum-agreement.py

import pathlib
import sys
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

BAR_COLOR = "#1f77b4"
CHANCE_COLOR = "#d62728"


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]

    # Sealed criterion: agreement across both calls per problem.
    by_problem = {}
    for r in records:
        by_problem.setdefault(r["problem_id"], []).append(r)
    strata = ("S1", "S2", "S3")
    labels = ["S1\n(delta >= 20%)", "S2\n(5% <= delta < 20%)", "S3\n(0.5% <= delta < 5%)"]
    rates, los, his, ns = [], [], [], []
    for s in strata:
        pids = [p["problem_id"] for p in problems["problems"]
                if oracle[p["problem_id"]]["stratum"] == s]
        k = sum(1 for pid in pids
                if all(r["agreement"] for r in by_problem[pid]))
        n = len(pids)
        lo, hi = a.wilson_interval(k, n)
        rates.append(k / n)
        los.append(lo)
        his.append(hi)
        ns.append(n)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(strata))
    err_low = [rates[i] - los[i] for i in x]
    err_high = [his[i] - rates[i] for i in x]
    ax.bar(x, rates, width=0.55, color=BAR_COLOR, label="Agreement rate")
    ax.errorbar(x, rates, yerr=[err_low, err_high], fmt="none",
                ecolor="black", capsize=5, label="Wilson 95% CI")
    ax.axhline(0.2, color=CHANCE_COLOR, linestyle="--", linewidth=1,
               label="Chance rate (1/5)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Both-call agreement rate (n=40 per stratum)")
    ax.set_title("v2.0.0 per-stratum agreement, judge jev-1.13.0")
    for i in x:
        ax.text(i, rates[i] + 0.03, f"{ns[i]}/{ns[i]}",
                ha="center", va="bottom", fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig1-stratum-agreement.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
