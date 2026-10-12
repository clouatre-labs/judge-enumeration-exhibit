# Conclusion of the Judge Enumeration Exhibit

Date: 2026-10-11
Scope: v1.0.0 stability phase through v2.0.0 discrimination phase
Basis: committed numbers only, from `experiments/judge-enumeration-v2/{endpoints.json, analysis.json}`, `experiments/judge-enumeration/`, and the raw records they derive from

The exhibit ran two pre-registered phases against the same class of
instrument, a typed probabilistic judge, on a frozen 3-variable linear
program task. This document states what the two phases jointly
establish, what they do not establish, and what a v2.1 would need. It
is interpretation, not new analysis; the endpoints are frozen and every
number below is a committed value.

## The two phases

*Table 1: Phases of the exhibit.*

| Phase | Preregistration | n | Question | Headline |
| --- | --- | --- | --- | --- |
| v1.0.0 stability | [preregistration.md](../preregistration.md) | 60 | Does the judge give stable answers to identical states? | Stable at the probed scale; raw sessions in `results/raw/` |
| v2.0.0 discrimination | [preregistration-v2.0.md](../preregistration-v2.0.md) | 240 (120 x 2 passes) | Can the judge discriminate optimal from near-optimal and infeasible candidates, per stratum? | 40/40 both-call agreement in every stratum; ceiling |

## What the exhibit establishes

1. **Stability.** The v1 phase probed run-to-run stability and the v2
   phase confirmed it at scale: 0/120 per-problem disagreements across
   two passes with a different presentation order. Typed probabilistic
   judges, as exemplified here, give reproducible selections on
   identical decision states.
2. **Discrimination, saturated.** In v2, both-call agreement is 40/40 in
   each stratum (Wilson 95% CI [0.912, 1.000]), prune failure is 0/240,
   and the position-bias check is flat at 1.000. The judge never fell
   for a super-optimal infeasible decoy, the exact failure mode the
   menu design sets up, and never favored a menu position.
3. **Calibration shape.** Brier score on the selected-option probability
   is 0.0251 and ECE over 5 equal-width bins is 0.1366. With accuracy
   at 1.0, both numbers measure only confidence shortfall: the judge is
   systematically less than certain about answers that are always
   right.

Jointly, the exhibit establishes for this instrument, and as a worked
example for the class: **stability without calibration evidence, and
discrimination that saturates at this difficulty.** That pairing is
itself informative. The failure mode a decision pipeline most needs to
rule out, silently picking an infeasible but higher-valued option, is
absent; the residual weakness is miscalibrated confidence, which is
observable and correctable at the consumer of the probabilities, not
hidden in the selections.

## What the exhibit does NOT establish

Per preregistration section (h), nothing here generalizes beyond its
design:

- One model version, `jev-1.13.0`. No cross-model claim is licensed.
- Menus were pre-enumerated by the oracle; the judge never enumerated
  candidates itself.
- Stratum boundaries (20%, 5%, 0.5%) are design choices, not estimated
  difficulty scales.
- The task class is d=3 integer linear programs; nothing follows for
  other dimensions or domains.
- n=2 replication bounds within-problem stability claims.

And per the ceiling, the exhibit does not establish graded difficulty
sensitivity. The Fisher exact S1-versus-S3 test (p = 1.0) is a ceiling
artifact; the strata never had a chance to differ. No claim of the form
"the judge handles 0.5% gaps as well as 20% gaps in general" is
supported; only "on these 120 menus it did" is.

## What a v2.1 would need

- **Harder menus.** Gaps below the current 0.5% floor, second-best
  vertices closer to ties, and possibly more candidates per menu to
  push the chance rate down.
- **Closer decoys.** Decoys that are nearly feasible (violating a
  constraint marginally) or nearly tied in objective value, so the
  feasibility check requires actual constraint evaluation rather than
  a visible violation.
- **A second model.** Cross-model replication is the single cheapest
  way to convert an instrument property into a class property; the v2.0
  pin defers this to v2.1 by design.
- **A difficulty axis that discriminates.** Any v2.1 endpoint set should
  be piloted so that at least one stratum fails to reach ceiling;
  otherwise the primary endpoint saturates again and the strata are
  uninformative a second time.

## Status

The exhibit is concluded at v2.0.0. Release v2.0.0 and DOI
10.5281/zenodo.23307259 archive the discrimination phase; the raw
records, sealed analysis, and figures reproduce from the repository.
