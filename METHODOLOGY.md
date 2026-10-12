# Methodology

Experimental design and analysis plan for experiments in this repository. Replace each `TODO` section per experiment; keep this top-level document as the shared methodological contract.

## Research Question

Can a typed probabilistic judge discriminate the optimal candidate from near-optimal and infeasible decoys in small linear-program menus, and are its answers stable across repeated calls? Phased so that a null result (agreement at or below chance) is as publishable as a positive one; the v2.0 phase saturated, which is reported as an instrument property, not a success of the judge (see [docs/conclusion.md](docs/conclusion.md)).

## v2.0 Discrimination Phase Pointer

The v2.0.0 phase has its own frozen contract: [preregistration-v2.0.md](preregistration-v2.0.md) fixes the 120-problem set, the model pin (`jev-1.13.0`), the sealed reading criterion (section d), and the endpoints (section e). The sealed criterion and endpoints are FROZEN: interpretation documents restate and interpret endpoint values but never re-derive, reinterpret, or extend the criterion; anything beyond a section (e) endpoint must be labeled exploratory. Derived numbers in documentation are recomputed exactly from raw records with Fraction arithmetic. No composite metrics are permitted anywhere in this repository. Raw records: `results/raw/v2/run-001..240.json`; sealed analysis: `experiments/judge-enumeration-v2/`; interpretation: [results/v2.md](results/v2.md).

## Pre-Registration

Every experiment MUST have its protocol, rubric, and scoring prompts committed under `experiments/<slug>/` BEFORE any session is run. The commit containing the pre-registration must precede the first run record; edits after data collection begins require a dated addendum in the experiment's `protocol.md`.

- Rubric criteria are defined before examining any model output.
- Group assignments are sealed in `label-map.json` before scoring begins.
- Statistical tests are named in the protocol before data collection.

## Experimental Design

TODO: Describe per experiment:

- Task and target (issue, dataset, or benchmark used).
- Groups: control and treatment conditions, with exact prompt text or deltas.
- Sample size per group and stopping rule.
- Agent or model configuration (model, temperature, provider, extensions).

## Blind Scoring

Scorers receive only the output artifacts and the rubric. No group labels, run metadata, or sibling outputs are visible during scoring. Report any inter-rater reliability checks and their agreement statistics.

## Analysis Plan

Analysis results land in `experiments/<slug>/analysis.json` (schema in [DATA_DICTIONARY.md](DATA_DICTIONARY.md), enforced by `validate_schema.py`). Scores with per-criterion justifications land in `scores.json`. Figures are generated from `recipe/` scripts into `figures/`.

## Threats to Validity

TODO: Enumerate, at minimum:

- Ceiling or floor effects in the rubric.
- Rubric-scorer co-design bias.
- Run-to-run variance and seed/provider nondeterminism.
- Contamination of the task in model training data.
