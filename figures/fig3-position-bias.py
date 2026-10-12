# SPDX-License-Identifier: Apache-2.0
# Position-bias check over menu positions, v2.0.0 discrimination phase.
# Agreement and prune-failure rates by optimal-candidate position,
# recomputed from the raw v2 run records plus the committed oracle with
# the sealed-criterion code in
# experiments/judge-enumeration-v2/analyze_v2.py. Render with:
#     uv run --with matplotlib python figures/fig3-position-bias.py

import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "judge-enumeration-v2"))
import analyze_v2 as a  # noqa: E402

AGREE_COLOR = "#1f77b4"
PRUNE_COLOR = "#d62728"


def main():
    oracle, problems, calls = a.load_inputs()
    records = [a.per_call_record(oracle, c) for c in calls]
    bias = a.position_bias(records)

    positions = [str(p) for p in range(1, 6)]
    agree = [bias[p]["agreement"] for p in positions]
    prune = [bias[p]["prune_failure"] for p in positions]
    ns = [bias[p]["n"] for p in positions]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(positions))
    ax.bar([i - 0.19 for i in x], agree, width=0.38, color=AGREE_COLOR,
           label="Agreement rate")
    ax.bar([i + 0.19 for i in x], prune, width=0.38, color=PRUNE_COLOR,
           label="Prune-failure rate")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"position {p}\n(n={n})" for p, n in zip(positions, ns)])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Rate over all 240 calls")
    ax.set_title("Position-bias check: optimal candidate at menu position 1-5")
    for i in x:
        ax.text(i - 0.19, agree[i] + 0.02, f"{agree[i]:.3f}",
                ha="center", va="bottom", fontsize=9)
        ax.text(i + 0.19, prune[i] + 0.02, f"{prune[i]:.3f}",
                ha="center", va="bottom", fontsize=9)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(__file__).resolve().parent / "fig3-position-bias.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
