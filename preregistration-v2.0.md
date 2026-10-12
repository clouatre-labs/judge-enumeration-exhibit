# Preregistration: Sealed Judge Enumeration Exhibit v2.0.0

Version: 2.0.0
Author: Hugues Clouatre (ORCID 0009-0002-4291-1999)
Frozen problem set: `problems-v2.json` (sha256
70b9679227528490809689c7ec66fffa2bcf55e6d38de2262e5c08610f430e29)

This document is committed before any judge response exists for any
v2.0 problem. It fixes the task, the generator, the model pin, the
sealed reading criterion, and the endpoints. Post-hoc edits require a
dated addendum.

## (a) Task

120 distinct 3-variable linear programs. For each problem the judge
state contains the objective vector c (integers 1-9), the constraint
system A x <= b (6 integer constraints: 3 upper bounds and 3
non-negativity), and a menu of exactly 5 candidates: 4 feasible
vertices (strictly including the global optimum v* and the second-best
feasible vertex v2) plus 1 infeasible super-optimal decoy. The state
carries NO objective values. The correct answer is the feasible
argmax of c^T x.

Instructions (verbatim):

> Which candidate production plan should be selected for this production decision, given the stated constraints and objective?

Per-option criteria (verbatim, one per candidate `<ID>` with
production levels `x=(x1, x2, x3)`):

> Candidate <ID>: production levels x=(x1, x2, x3).

## (b) Generator specification

`generate_problems.py` implements this spec; the seeded output is
committed as `problems-v2.json` (hash above) with seed 20260214, and
the analysis-side oracle values as `oracle-v2.json`.

- Seeded PRNG with the fixed seed committed with the problem set;
  identical seed reproduces the identical set bit for bit.
- d=3; all coordinates in [0,50]; menu vertices are integers.
- The LP may have M >= 4 extreme points; the oracle places exactly
  4 feasible vertices plus 1 decoy in the menu.
- The decoy satisfies c^T x_decoy > c^T v* (super-optimal trap:
  skipping the feasibility check guarantees a wrong answer).
- Decoy domain invariant: x_decoy in [0,50]^3 with infeasibility
  arising ONLY from upper-bound violations, never from non-negativity
  or range.
- Strict unique optimum; alternative optima are rejected.
- Strata by Delta = (z* - z2)/z*: S1 Delta >= 20% (n=40), S2
  5% <= Delta < 20% (n=40), S3 0.5% <= Delta < 5% (n=40).
- Integer quantization: z values are integers, so Delta = k/z* with
  integer k = z* - z2; target z* >= 21; k = 1 is rejected when
  z* > 200. Rejection counts are committed with the problem set.
- Within-stratum position balancing: the optimal candidate occupies
  each rank position 1-5 exactly 8 times per stratum; the decoy
  position is uniform across positions (8 per position per stratum);
  optimum and decoy are never co-located.

## (c) Model pin

Pinned model: `jev-1.13.0` (an explicit version, never an alias). The
tool exposes no temperature control; provider defaults apply, and no
default temperature has been published, so none is stated. This is a
single-model phase; a second model is deferred to a possible v2.1.

## (d) Sealed reading criterion v2

The following criterion is recorded BEFORE any judge response is
examined.

- Per-call record: the selected option id, the selected-option
  probability, and all option probabilities.
- Agreement: a call agrees when the selected id equals the oracle
  argmax over feasible candidates.
- Prune failure: the selected id is the decoy.
- Per-problem stability: agreement across the 2 calls per problem.
- Chance rate: 1/5.

## (e) Endpoints

Fixed before any call. All outcomes are publishable.

- Primary: per-stratum agreement rate (n=40 per stratum) with Wilson
  95% confidence intervals, and a pre-specified two-sided Fisher exact
  test of S1 versus S3.
- Secondary: prune-failure rate (overall and per stratum),
  per-problem disagreement rate (across the 2 calls), Brier score on
  the selected-option probability (primary calibration measure), expected
  calibration error with 5 equal-width bins (secondary), and a
  position-bias check over menu positions.
- Anything else is exploratory and must be labeled as such.

## (f) Runner

`run_judge.py` is extended to accept per-problem states (schema
superset, backward compatible with the v1.x `frozen_state.json`).
The 240 calls (120 problems x 2) execute as TWO PASSES: pass 1 runs
problems 1-120 in committed order; pass 2 runs problems 1-120 under a
distinct seed-derived permutation, committed in
`problems-v2.json` as `pass2_order`. The pass id is logged per call.
Each call records its verbatim request and response to
`results/raw/v2/run-NNN.json` (run 001-240). The call log is
append-only. Fallback envelopes (`{"fallback": true, "error": ...}`)
are recorded and counted, never silently skipped; the runner exits
non-zero if any call falls back. The runner refuses to overwrite an
existing raw record. In this phase the extension is CODE only and is
verified via `--dry-run` exclusively; no call is made before this
preregistration and the problem set are merged to main.

## (g) Transparency note

"The protocol author maintains the judge tool under test
(decisions-judge-mcp). The judge is treated as an instance of the
general class 'typed probabilistic judge'; findings are about the
exhibit, not the product. Public artifacts enable independent
verification."

## (h) Pre-acknowledged limitations

- Single model version; no cross-model generalization claim.
- Menus are pre-enumerated by the oracle, not discovered by the judge.
- Stratum boundaries (20%, 5%, 0.5%) are design choices, not
  nature-estimated thresholds.
- d=3 integer class only; no claim beyond this class.
- n=2 within-problem replication bounds within-problem stability
  claims.

## (i) Commit ordering

This preregistration, the generator, the frozen problem set, and the
tests are committed BEFORE any v2.0 judge call. Calls are made only
after this phase is merged to main, in the two passes of section (f).
