"""Deterministic generator for the v2.0 judge-enumeration problem set.

Implements the generator specification in preregistration-v2.0.md
section (b): 120 distinct 3-variable LPs in three strata by relative
optimality gap Delta=(z*-z2)/z*, each with a 5-candidate menu of 4
feasible vertices (strictly including the optimum v* and second-best
v2) plus 1 infeasible super-optimal decoy.

All arithmetic is exact: vertex objectives are integer combinations of
integer coordinates, and Delta is compared as a Fraction. Judge-facing
candidate fields carry id and x only; objective values live in the
separate oracle file.

Usage:
    python3 generate_problems.py                       # print summary
    python3 generate_problems.py --emit                # write problems-v2.json and oracle-v2.json
"""

import argparse
import json
import random
import sys
from fractions import Fraction

SEED = 20260214
N_PROBLEMS = 120
STRATA = ("S1", "S2", "S3")
N_PER_STRATUM = 40
COORD_MAX = 50
B_MIN = 5
B_MAX = 50
C_MIN = 1
C_MAX = 9
Z_STAR_MIN = 21

# Exact stratum thresholds on Delta = k / z*.
DELTA_S1 = Fraction(1, 5)      # Delta >= 20%
DELTA_S2 = Fraction(1, 20)     # 5% <= Delta < 20%
DELTA_S3 = Fraction(1, 200)    # 0.5% <= Delta < 5%

REJECTION_REASONS = (
    "tied_optimum",
    "z_star_below_min",
    "k1_with_large_z_star",
    "delta_below_floor",
    "decoy_domain",
)

# Upper bounds (rows 0-2) and non-negativity (rows 3-5) as A x <= b.
A_ROWS = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
    [-1, 0, 0],
    [0, -1, 0],
    [0, 0, -1],
]


def feasible(x, b):
    """Exact feasibility of integer x against the 6 stated constraints."""
    for row, bound in zip(A_ROWS, b):
        if sum(a * v for a, v in zip(row, x)) > bound:
            return False
    return True


def violates_upper_bounds_only(x, b):
    """True when x satisfies non-negativity but breaks >=1 upper bound."""
    if any(v < 0 for v in x):
        return False
    return any(
        sum(a * v for a, v in zip(row, x)) > bound
        for row, bound in zip(A_ROWS[:3], b[:3])
    )


def corners(b):
    """The 8 box vertices of [0,b1]x[0,b2]x[0,b3]."""
    return [
        (b[0] if i & 1 else 0, b[1] if i & 2 else 0, b[2] if i & 4 else 0)
        for i in range(8)
    ]


def objective(c, x):
    return sum(ci * xi for ci, xi in zip(c, x))


def decoy_point(c, x_star, b, rng):
    """Super-optimal infeasible point: bump one coordinate past its bound."""
    axes = [j for j in range(3) if b[j] < COORD_MAX]
    if not axes:
        return None
    j = rng.choice(axes)
    x = list(x_star)
    x[j] = rng.randint(b[j] + 1, COORD_MAX)
    return tuple(x)


def position_schedule():
    """40 (optimum_position, decoy_position) pairs (0-based), v* at each
    position exactly 8 times, decoy at each position exactly 8 times,
    never co-located: n[i][j]=2 for every i != j."""
    pairs = []
    for slot in range(N_PER_STRATUM):
        vpos = slot % 5
        dpos = (vpos + (slot // 5 % 4) + 1) % 5
        pairs.append((vpos, dpos))
    return pairs


def stratum_of(delta):
    if delta >= DELTA_S1:
        return "S1"
    if delta >= DELTA_S2:
        return "S2"
    if delta >= DELTA_S3:
        return "S3"
    return None


def draw_problem(rng):
    """One rejection-sampled LP. Returns None (with rejection recorded by
    the caller via reason) or a dict of exact problem data."""
    c = [rng.randint(C_MIN, C_MAX) for _ in range(3)]
    b = [rng.randint(B_MIN, B_MAX) for _ in range(3)]
    zs = sorted((objective(c, x) for x in corners(b)), reverse=True)
    z_star, z_second = zs[0], zs[1]
    k = z_star - z_second
    if k == 0:
        return None, "tied_optimum"
    if k == 1 and z_star > 200:
        return None, "k1_with_large_z_star"
    if z_star < Z_STAR_MIN:
        return None, "z_star_below_min"
    delta = Fraction(k, z_star)
    stratum = stratum_of(delta)
    if stratum is None:
        return None, "delta_below_floor"
    return (c, b, z_star, z_second, k, delta, stratum), None


def generate(seed=SEED):
    """Generate the full committed problem set. Returns (problems, oracle,
    rejection_counts, stats)."""
    rng = random.Random(seed)
    rejections = {reason: 0 for reason in REJECTION_REASONS}
    pools = {s: [] for s in STRATA}
    schedules = {s: position_schedule() for s in STRATA}
    for s in STRATA:
        rng.shuffle(schedules[s])

    # Phase 1: fill stratum pools with exact LP data.
    while any(len(pools[s]) < N_PER_STRATUM for s in STRATA):
        result, reason = draw_problem(rng)
        if result is None:
            rejections[reason] += 1
            continue
        c, b, z_star, z_second, k, delta, stratum = result
        if len(pools[stratum]) >= N_PER_STRATUM:
            continue
        target = schedules[stratum][len(pools[stratum])]
        vpos, dpos = target
        cs = corners(b)
        scored = sorted(cs, key=lambda x: objective(c, x), reverse=True)
        x_star, x_second = scored[0], scored[1]
        others = [x for x in scored[2:] if x != x_second][:2]
        x_decoy = decoy_point(c, x_star, b, rng)
        if x_decoy is None:
            rejections["decoy_domain"] += 1
            continue
        pools[stratum].append(
            {
                "c": c,
                "b": b,
                "z_star": z_star,
                "z_second": z_second,
                "k": k,
                "delta": delta,
                "x_star": x_star,
                "x_second": x_second,
                "x_others": others,
                "x_decoy": x_decoy,
                "vpos": vpos,
                "dpos": dpos,
            }
        )

    # Phase 2: assemble committed problem order S1 -> S2 -> S3.
    problems = []
    oracle = {}
    for s in STRATA:
        for item in pools[s]:
            pid = "p-%03d" % (len(problems) + 1)
            menu = [None] * 5
            menu[item["vpos"]] = ("v_star", item["x_star"])
            menu[item["dpos"]] = ("decoy", item["x_decoy"])
            fillers = [("v_second", item["x_second"])] + [
                ("other", x) for x in item["x_others"]
            ]
            rng.shuffle(fillers)
            fill_iter = iter(fillers)
            menu = [
                menu[i] if menu[i] is not None else next(fill_iter)
                for i in range(5)
            ]
            candidates = [
                {"id": chr(65 + i), "x": [int(v) for v in x]} for i, (_, x) in enumerate(menu)
            ]
            problems.append(
                {
                    "problem_id": pid,
                    "stratum": s,
                    "c": item["c"],
                    "A": [list(r) for r in A_ROWS],
                    "b": list(item["b"]) + [0, 0, 0],
                    "candidates": candidates,
                }
            )
            oracle[pid] = {
                "stratum": s,
                "optimal_id": chr(65 + item["vpos"]),
                "decoy_id": chr(65 + item["dpos"]),
                "second_best_id": next(
                    cid
                    for cid, role in (
                        (cand["id"], role)
                        for (role, _), cand in zip(menu, candidates)
                    )
                    if role == "v_second"
                ),
                "z_star": item["z_star"],
                "z_second": item["z_second"],
                "delta_k": item["k"],
                "delta_z_star": item["z_star"],
                "objective_values": {
                    cand["id"]: objective(item["c"], cand["x"])
                    for cand in candidates
                },
                "roles": {
                    cand["id"]: role
                    for (role, _), cand in zip(menu, candidates)
                },
            }
    return problems, oracle, dict(rejections)


def build_document(seed=SEED):
    problems, oracle, rejections = generate(seed)
    rng = random.Random(seed + 1)
    pass2_order = list(p["problem_id"] for p in problems)
    rng.shuffle(pass2_order)
    doc = {
        "version": "2.0.0",
        "seed": seed,
        "pass2_order": pass2_order,
        "rejection_counts": rejections,
        "problems": problems,
    }
    return doc, oracle


def summarize(doc, oracle):
    lines = []
    lines.append("problems: %d" % len(doc["problems"]))
    for s in STRATA:
        n = sum(1 for p in doc["problems"] if p["stratum"] == s)
        lines.append("%s: n=%d" % (s, n))
    lines.append("rejections: %s" % json.dumps(doc["rejection_counts"], sort_keys=True))
    s3 = [
        Fraction(o["delta_k"], o["delta_z_star"])
        for o in oracle.values()
        if o["stratum"] == "S3"
    ]
    lines.append("S3 min delta: %s (%.4f%%)" % (min(s3), float(min(s3)) * 100))
    lines.append("S3 max delta: %s" % max(s3))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="v2.0 problem set generator (deterministic)."
    )
    parser.add_argument(
        "--emit",
        action="store_true",
        help="write problems-v2.json and oracle-v2.json",
    )
    args = parser.parse_args()
    doc, oracle = build_document()
    print(summarize(doc, oracle))
    if args.emit:
        with open("problems-v2.json", "w") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")
        with open("oracle-v2.json", "w") as f:
            json.dump(oracle, f, indent=2)
            f.write("\n")
        print("wrote problems-v2.json and oracle-v2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
