# Protocol: judge-enumeration

Pre-registered before any run. The full sealed question, model pin,
and reading criterion live in the repository root
[preregistration.md](../../preregistration.md) (version-stamped v1.0.0);
this file points to it and records the exhibit-specific design.

- Task: choice-type arbitration over the pre-enumerated feasible
  vertices of a 3-variable blending LP, frozen in `frozen_state.json`
  (sha256 recorded in preregistration.md).
- Groups: single arm; every run uses the identical preregistered
  question and state (no control/treatment contrast in this exhibit).
- Sample size: 5 sequential judge calls with model `jev-1.13.0`.
- Statistical test: descriptive; per-run agreement with the exact
  optimum M*=14480 and modal-option consistency across the 5 runs,
  as fixed by the sealed reading criterion.
- Scoring: the sealed reading criterion in preregistration.md section
  (d), applied to the recorded raw responses before any aggregate is
  computed.
- Threats to validity: n=5 bounds claims to variance/stability, not
  calibration; the state presents pre-enumerated vertices, not raw
  constraints; no temperature control is exposed (provider defaults
  apply).

## Result-dependent fields

`analysis.json` and `scores.json` in this directory were committed in
the pre-registration commit in a schema-valid pre-run state (zero
runs). They have been updated in the post-run PR from
`results/raw/run-01.json` .. `results/raw/run-05.json`: the five run
records (`treatment_1` .. `treatment_5`), their scores under the
sealed reading criterion, and the final conclusion. The sealed reading
criterion and its outcome are recorded in
[findings.md](findings.md). No judge result was fabricated.
