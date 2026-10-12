# Findings: v2.0.0 discrimination phase

Experiment: judge-enumeration-v2
Preregistration: preregistration-v2.0.md (merged to main at bf95cf3 before any call)
Model: jev-1.13.0
Runs: 240 (120 problems x 2 passes); runs 1-120 pass 1 in committed problem order, runs 121-240 pass 2 under the committed pass2_order permutation. Per-call pass ids are recorded in experiments/judge-enumeration-v2/endpoints.json and analysis.json so two-pass execution is verifiable. All 240 calls succeeded with fallback=false.

This is a discrimination result. All three outcome shapes (agreement above chance, at chance, below chance) were publishable under the preregistration; the observed outcome is the first shape.

## Primary endpoint

Per-stratum agreement rate, n=40 per stratum, where agreement means the judge selected the optimal feasible candidate across both calls per problem (sealed reading criterion v2, section (d)). Chance rate is 1/5.

| Stratum | Agreement rate | Wilson 95% CI |
| --- | --- | --- |
| S1 (delta >= 20%) | 40/40 = 1.000 | [0.912, 1.000] |
| S2 (5% <= delta < 20%) | 40/40 = 1.000 | [0.912, 1.000] |
| S3 (0.5% <= delta < 5%) | 40/40 = 1.000 | [0.912, 1.000] |
| Overall (n=120) | 120/120 = 1.000 | [0.969, 1.000] |

Pre-specified two-sided Fisher exact test, S1 versus S3: p = 1.0. There is no detectable difference between strata because every problem in every stratum was solved; the test is uninformative in the ceiling direction, not evidence of equality of difficulty.

Per-call agreement over all 240 calls (exploratory): 240/240 = 1.000, Wilson 95% CI [0.984, 1.000].

## Secondary endpoints

- Prune-failure rate (selected id equals the infeasible super-optimal decoy): 0/240 = 0.000 overall; 0/40 in each of S1, S2, S3. The decoy was never selected; the feasibility check that the decoy is designed to trap was never skipped.
- Per-problem disagreement across the 2 calls: 0/120 = 0.000. The run is perfectly stable under the pass-2 permutation.
- Brier score on the selected-option probability (primary calibration): 0.0251. With perfect discrimination this equals the mean squared shortfall of the selected probability from 1.
- Expected calibration error, 5 equal-width bins (secondary): 0.1366.
- Position-bias check over menu positions: agreement is 1.000 and prune failure is 0.000 at every optimal-candidate position 1 through 5 (n=48 calls per position). No position bias is detectable.

## Framing

The judge achieves perfect discrimination on this exhibit: every one of the 120 frozen 3-variable linear programs was solved identically in two passes, the super-optimal infeasible decoy was never chosen, and confidence is high but not certain (mean selected-option probability 0.8634, recomputed from the raw records with Fraction arithmetic, with Brier 0.0251). The nonzero ECE reflects mild overconfidence in an otherwise perfect run: accuracy is 1.0 so any probability below 1.0 contributes calibration error, and the ECE is bounded by 1 minus mean confidence rather than by any misranking.

## Provenance and naivete

The committed run was fully naive: all 240 calls were executed after the preregistration and frozen problem set were merged to main at bf95cf3, per section (i). One pre-merge deviation is disclosed in the dated addendum to preregistration-v2.0.md: 120 smoke responses produced before merge by an incomplete argument guard were deleted without examination; no response content from them entered the analysis, the repository, or any artifact, and they are not part of n=240.

## Method note

All rates, Wilson intervals, the Fisher exact test, the Brier score, and the ECE were computed with exact Fraction arithmetic in experiments/judge-enumeration-v2/analyze_v2.py and converted to float only at output. Recompute with:

    python3 experiments/judge-enumeration-v2/analyze_v2.py
