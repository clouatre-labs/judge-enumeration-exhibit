# Preregistration: Sealed Judge Enumeration Exhibit v1.0.0

Version: 1.0.0
Author: Hugues Clouatre (ORCID 0009-0002-4291-1999)
Frozen state: `frozen_state.json` (sha256
17e2c5593c9628f527cb4b8f88f630086bd10859d07599443a002f19bfe339c2)

This document is committed before any judge response exists. It fixes
the question, the model pin, and the reading criterion. Post-hoc edits
require a dated addendum.

## (a) Judge question

Question type: choice. Predicate: positive (the judge selects one
option, it does not rank or rate). Single trait: production plan
selection. No secondary qualitative priority is provided; the locked
criterion is pure objective maximization.

Instructions (verbatim):

> Which candidate production plan should be selected for this blending decision?

Per-option criteria (verbatim, one per candidate `<ID>` with objective
value `<V>` and production levels `x=(x1,x2,x3)`):

> Select the plan with objective value <V> at production levels x=(x1,x2,x3) (candidate <ID>)

The locked criterion is pure objective maximization. The correct
answer is candidate G, x=(9.2, 6, 4), with objective value M*=14480.

## (b) Frozen state integrity

The judge receives the exact contents of `frozen_state.json`, generated
by `enumerate.py --emit-state` (exact Fraction arithmetic, deterministic
ascending sort by (x1, x2, x3)). Its sha256 at preregistration time is
recorded above; any change to the file invalidates this preregistration.

## (c) Model pin

Pinned model: `jev-1.13.0` (an explicit version, never an alias). The
tool exposes no temperature control; provider defaults apply, and no
default temperature has been published, so none is stated.

## (d) Sealed reading criterion

The following criterion is recorded BEFORE any judge response is
examined.

- Per-run record: the selected option id for each of the 5 runs.
- Agreement: a run agrees with the exact optimum when the selected id
  is the M*=14480 candidate (candidate G).
- Consistency: the count of runs selecting the modal option (the
  option id chosen most often across the 5 runs).
- Both outcomes are publishable: observed variance AND observed
  stability are findings ("stability, not quality"). A flat
  distribution across the 5 repeats (no modal option with at least 2
  runs) is a REPORTED finding, read as a question
  under-specification signal; it is not a discarded run.
- n=5 bounds all claims to variance/stability of the judge under this
  question; it supports no claim about calibration or accuracy.

## (e) Transparency note

"The protocol author maintains the judge tool under test
(decisions-judge-mcp). The judge is treated as an instance of the
general class 'typed probabilistic judge'; findings are about the
exhibit, not the product. Public artifacts enable independent
verification."

## (f) Runner fallback semantics

`run_judge.py`'s retry/fallback handling is a documented
reimplementation of the SDK's fallback envelope semantics
(`{"fallback": true, "error": ...}`). A fallback envelope is recorded
in the call log and counted, never silently skipped; the runner exits
non-zero if any call falls back.

## (g) State presentation

The frozen state presents pre-enumerated feasible vertices (35 raw
constraint-triple intersections reduced to 7 by the exact feasibility
filter and deduplication) as an arbitration task, not raw constraints.
The judge never sees the constraint system itself.
