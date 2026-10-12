# v2.0 Generator Acceptance Report

Generator: `generate_problems.py`, seed 20260214. Problem set:
`problems-v2.json` (sha256
70b9679227528490809689c7ec66fffa2bcf55e6d38de2262e5c08610f430e29).
All values below are produced by `python3 generate_problems.py`.

## Acceptance counts

| Stratum | Definition | n |
|---------|------------|---|
| S1 | Delta >= 20% | 40 |
| S2 | 5% <= Delta < 20% | 40 |
| S3 | 0.5% <= Delta < 5% | 40 |
| Total | | 120 |

## Rejection counts

| Reason | Count |
|--------|-------|
| tied_optimum | 0 |
| z_star_below_min (z* < 21) | 0 |
| k1_with_large_z_star | 0 |
| delta_below_floor | 0 |
| decoy_domain | 0 |

Draws that land in a stratum whose quota of 40 is already filled are
discarded silently; they are not invariant rejections and are not
counted above.

## S3 feasibility of the 0.5% floor

The S3 floor is reachable: the smallest committed S3 gap is
Delta = 3/241, about 1.2448%, comfortably above the 0.5% floor and
below the 5% ceiling. The largest S3 gap is 19/388, about 4.897%.
Integer quantization (Delta = k/z* with k = z* - z2 >= 1) permits
gaps as small as 1/z*, and no committed problem requires k = 1 with
z* > 200 (the pre-registered rejection rule), so the floor is
satisfiable within the committed set.

## Invariant verification

Verified by `test_generate_problems.py` (all passing):

- Determinism: identical seed reproduces identical JSON.
- 40 problems per stratum; 120 total.
- Every menu is 5 candidates with id and x only; no objective values
  in judge-facing fields.
- Every feasible candidate satisfies all 6 stated constraints; the
  decoy violates at least one upper bound while satisfying
  non-negativity and the [0,50]^3 domain.
- Every decoy is super-optimal (c^T x_decoy > z*).
- Strict unique optimum per problem; z* >= 21 throughout.
- Position balancing exact: per stratum, the optimum occupies each
  menu position 8 times and the decoy occupies each position 8
  times; optimum and decoy are never co-located.
- `pass2_order` is a committed derangement-free permutation of all
  120 problem ids.
