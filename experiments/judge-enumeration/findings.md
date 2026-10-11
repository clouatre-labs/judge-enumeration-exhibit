# Findings: judge-enumeration (sealed analysis, v1.0.0)

This document applies the sealed reading criterion from
[preregistration.md](../../preregistration.md) section (d) exactly as
written, to the five recorded judge responses in
[results/raw](../../results/raw/). No criterion was re-derived or
reinterpreted; every number below comes from the raw records.

## Setup

- Question: choice-type arbitration over the 7 feasible LP vertices
  frozen in `frozen_state.json`; locked criterion is pure objective
  maximization; exact optimum is candidate G at x=(9.2, 6, 4) with
  M* = 14480.
- Model: `jev-1.13.0` (pinned), provider-default sampling.
- Runs: 5 sequential calls, timestamps 2026-10-11T23:23:19+00:00
  through 2026-10-11T23:23:20+00:00.
- Fallback envelopes: 0 of 5 calls (results/calls.jsonl, all
  `"fallback": false`).

## Per-run agreement (sealed criterion)

| Run | Selected id | Confidence | G probability | Agrees with optimum (G, M*=14480) | Modal option consistency |
|-----|-------------|------------|---------------|-----------------------------------|--------------------------|
| treatment_1 | G | 0.86 | 0.88 | yes | yes |
| treatment_2 | G | 0.85 | 0.87 | yes | yes |
| treatment_3 | G | 0.91 | 0.92 | yes | yes |
| treatment_4 | G | 0.88 | 0.90 | yes | yes |
| treatment_5 | G | 0.87 | 0.89 | yes | yes |

- Agreement: 5/5 runs selected the M* = 14480 candidate (G).
- Consistency: 5/5 runs selected the modal option (G, chosen in all
  5 runs).
- Distribution: not flat; a modal option exists with at least 2 runs.

## Reading: stability, not quality

Both outcomes are publishable under the sealed criterion; here the
observed outcome is stability. The judge was stable across the 5
repeats under this question. This is a finding about stability of the
judge under this exhibit, not a finding about quality, calibration,
or accuracy.

## Limitations

- n=5 bounds all claims to variance/stability of the judge under this
  question; it supports no claim about calibration or accuracy.
- The frozen state presents pre-enumerated feasible vertices, not raw
  constraints.
- No temperature control is exposed; provider defaults apply and none
  is published.

## Transparency note

"The protocol author maintains the judge tool under test
(decisions-judge-mcp). The judge is treated as an instance of the
general class 'typed probabilistic judge'; findings are about the
exhibit, not the product. Public artifacts enable independent
verification."
