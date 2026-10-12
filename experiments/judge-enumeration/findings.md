# Findings: judge-enumeration (sealed analysis, n=60)

This document applies the sealed reading criterion from
[preregistration.md](../../preregistration.md) section (d) exactly as
written, to the sixty recorded judge responses in
[results/raw](../../results/raw/). No criterion was re-derived or
reinterpreted; every number below comes from the raw records. The
sample comprises the v1.0.0 phase (run-01..run-05) and the v1.1.0
post-hoc extension phase (run-06..run-60) authorized by the dated
addendum v1.1.0, which was committed before any extension call was
made.

## Setup

- Question: choice-type arbitration over the 7 feasible LP vertices
  frozen in `frozen_state.json`; locked criterion is pure objective
  maximization; exact optimum is candidate G at x=(9.2, 6, 4) with
  M* = 14480.
- Model: `jev-1.13.0` (pinned), provider-default sampling.
- Runs: 60 sequential calls. v1.0.0 phase: 5 calls, timestamps
  2026-10-11T23:23:19+00:00 through 2026-10-11T23:23:20+00:00.
  v1.1.0 extension phase: 55 calls, timestamps 2026-10-12T00:04:39+00:00
  (run-06) through 2026-10-12T00:04:51+00:00 (run-60).
- Fallback envelopes: 0 of 60 calls (results/calls.jsonl, all
  `"fallback": false`).
- Request identity: all 60 request bodies are byte-identical to the
  single v1.0.0 request (verified via canonical JSON over the request
  objects in results/raw/*.json).

## Aggregate results (sealed criterion)

- Distribution: G=60, all other candidates 0. The distribution is not
  flat; the modal option is G with 60 of 60 runs.
- Agreement with the exact optimum (G, x=(9.2, 6, 4), M*=14480):
  60/60 runs.
- Modal consistency: 60/60 runs selected the modal option (G).
- Confidence: min 0.84, max 0.91, mean 0.870.
- G probability: min 0.86, max 0.92, mean 0.890.

## Per-phase breakdown

| Phase | Runs | Selected G | Agrees with optimum | Modal consistency | Head at run time |
|-------|------|------------|---------------------|-------------------|------------------|
| v1.0.0 (run-01..run-05) | 5 | 5/5 | 5/5 | 5/5 | 4d19810b8c7ad0c6c2ee1a8d8740cc9f203b694c |
| v1.1.0 extension (run-06..run-60) | 55 | 55/55 | 55/55 | 55/55 | 8b3c25bef49b42176f9eacdc1cefe2bc521fc99d |
| Combined | 60 | 60/60 | 60/60 | 60/60 | see per-phase heads |

Per-phase confidence summaries:

- v1.0.0 (n=5): confidence min 0.85, max 0.91, mean 0.874; G
  probability min 0.87, max 0.92, mean 0.892.
- v1.1.0 extension (n=55): confidence min 0.84, max 0.91, mean 0.870;
  G probability min 0.86, max 0.92, mean 0.890.

## Reading: stability, not quality

Both outcomes are publishable under the sealed criterion; here the
observed outcome is stability. The judge was stable across the 60
repeats under this question, in both phases. This is a finding about
stability of the judge under this exhibit, not a finding about
quality, calibration, or accuracy. The n=60 sample still supports no
claim about calibration or accuracy.

## Limitations

- n=60 bounds all claims to variance/stability of the judge under
  this question; it supports no claim about calibration or accuracy.
- The v1.1.0 extension is a post-hoc sample-size extension per the
  dated addendum v1.1.0: the five v1.0.0 responses had been observed
  and analyzed when the addendum was committed, so the extension is a
  replication, not a confirmatory test.
- All 60 request bodies were byte-identical to the v1.0.0 request
  (verified via canonical JSON), so the sample probes one question
  phrasing only; no robustness across rephrasings is established.
- One accidental pre-commit verification call was made while checking
  the runner overwrite guard, before the addendum commit; its response
  was discarded and never logged. It is not counted and cannot affect
  this analysis; it is disclosed in the addendum for transparency.
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
