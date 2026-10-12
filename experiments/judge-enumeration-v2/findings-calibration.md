# Findings: stratified calibration addendum (post-hoc)

Experiment: judge-enumeration-v2
Status: post-hoc, non-preregistered exploratory analysis; no preregistered endpoint is changed
Basis: committed records only; `scripts/stratified-calibration.py` re-derives every number below from `results/raw/v2/run-001..240.json`, `problems-v2.json`, and `oracle-v2.json` via the sealed-criterion code in `analyze_v2.py`, with exact Fraction arithmetic throughout (entropy and Pearson correlations require `log2`/`sqrt` and are computed in float); output lands in `experiments/judge-enumeration-v2/calibration.json`

## Post-hoc disclosure

This analysis was not preregistered; it was identified after the sealed v2.0.0 reading while preparing the companion post. It is reported as exploratory with the stratum-level caveat below, and it changes no preregistered endpoint. The sealed v2.0.0 analysis (`findings.md`, `endpoints.json`) reported only pooled confidence summaries (Brier 0.0251, ECE 0.1366); the per-stratum gradient documented here is a hidden structure in the same 240 raw records that the pooled framing did not surface.

## Finding 1: confidence tracks difficulty monotonically although selections never flip

Selections are identical across strata (240/240 agreement, sealed result), but the probability mass the judge puts on its selected option decreases monotonically with difficulty, whether read from the option-probability table or from the stated confidence.

*Table 1: Per-stratum confidence statistics over 80 calls per stratum (40 problems x 2 passes), from `calibration.json`.*

| Stratum | Selected-option prob, mean (sd) | Stated confidence, mean (sd) |
| --- | --- | --- |
| S1 (gap >= 20%) | 0.894 (0.071) | 0.867 (0.089) |
| S2 (5% <= gap < 20%) | 0.858 (0.079) | 0.821 (0.099) |
| S3 (0.5% <= gap < 5%) | 0.838 (0.082) | 0.797 (0.102) |

The S1 versus S3 Welch contrast on stated confidence is 0.070 with SE 0.015 and t = 4.63 (n = 80 per stratum); on selected-option probability it is 0.056 with SE 0.012 and t = 4.63. The gradient is smooth: every step S1 to S2 to S3 moves down, and the strata never overlap in mean on either measure.

## Finding 2: the non-selected mass is structured

The probability the judge withholds from its selection is not noise; it is ordered by difficulty.

*Table 2: Per-stratum structure of the non-selected mass (runner-up = largest non-selected probability), from `calibration.json`.*

| Stratum | Runner-up prob, mean | Runner-up prob, max | Mean entropy (bits) |
| --- | --- | --- | --- |
| S1 | 0.053 | 0.17 | 0.625 |
| S2 | 0.069 | 0.18 | 0.784 |
| S3 | 0.082 | 0.26 | 0.859 |

Runner-up mass grows and mean entropy rises by about 0.23 bits from S1 to S3: as menus tighten, the judge spreads probability toward the near-optimal competitors, exactly the structure a graded instrument should show.

## Finding 3: infeasible decoy mass is flat across strata

The probability on the infeasible super-optimal decoy is essentially constant across strata: mean 0.015 (S1), 0.020 (S2), 0.017 (S3), with maxima 0.13, 0.15, 0.13. Infeasibility detection is gap-independent in these records; the decoy mass does not inherit the difficulty gradient that the feasible near-optimal candidates attract.

## Caveats

- **Stratum-level, not instance-level.** Within each stratum, the correlation of relative gap with selected-option probability is approximately zero (S1 r = -0.107, S2 r = +0.091, S3 r = -0.059). The pooled r = 0.273 is driven by the stratum means, not by instance-level difficulty sensitivity. The finding licenses a claim about strata, not about individual menus.
- **Pass-to-pass drift exists despite identical argmax.** The selected option never changes between passes, but the probabilities do: mean |delta p_top| = 0.0245, max 0.11, and only 14% of problems (17/120) return the exact same p_top. Probabilities are quantized to 0.01 steps (the full histogram is in `calibration.json`), so the drift is at the resolution of the quantizer rather than at the argmax.

## No latency data

The v2 raw records contain no latency information; `output_tokens` is constant at 52 per call. No latency analysis is possible or attempted.

## Headroom note for v2.1

The minimum selected-option probability in S3 is 0.63: even on the hardest stratum, the judge retains measurable room to degrade before selections would flip at the 1/5 chance boundary. Harder menus in a v2.1 have quantified headroom; the confidence gradient documented here can worsen considerably before the primary endpoint saturates no longer, which is why a v2.1 pilot must include a graded-confidence endpoint rather than relying on selection flips alone.

## Reproduction

```sh
python3 scripts/stratified-calibration.py
```

The output `experiments/judge-enumeration-v2/calibration.json` contains per-stratum and pooled statistics, both S1 versus S3 Welch contrasts, within-stratum and pooled correlations, drift statistics, and the quantization histogram.
