# Data Dictionary

This document defines the schema and field meanings for experiment data files in this repository. `validate_schema.py` enforces the required fields below; run `uv run python validate_schema.py` before every PR that touches `experiments/`.

## Layout

Each experiment directory `experiments/<slug>/` contains:

- `analysis.json`: run metadata, message counts, and evaluation scores (schema below)
- `scores.json`: per-criterion rubric scores with justifications
- `protocol.md`, `runner-prompt.md`, `scorer-prompt.md`: pre-registration artifacts
- `sessions/`: raw session logs or database exports

## analysis.json

### Top-level schema

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `experiment` | string | no | Experiment slug, matches the directory name |
| `schema_version` | string | no | Version of this schema the record conforms to |
| `title` | string | no | Human-readable experiment title |
| `issue` | string \| null | yes | Target issue or task reference |
| `date` | string | no | Experiment date (YYYY-MM-DD) |
| `model` | string | no | Model identifier under test |
| `n_per_group` | integer | no | Number of runs per group |
| `control_condition` | string | no | Description of the control condition |
| `treatment_condition` | string | no | Description of the treatment condition |
| `rubric_version` | string | no | Rubric identifier used for scoring |
| `orchestrator_session` | string \| null | yes | Orchestrator session reference, if any |
| `repo_head` | string | no | Repository commit at run time |
| `experiment_start` | string | no | ISO 8601 timestamp with UTC offset of first run |
| `experiment_end` | string | no | ISO 8601 timestamp with UTC offset of last run |
| `analyzed_at` | string | no | ISO 8601 timestamp with UTC offset of analysis |
| `runs` | object | no | Map of run ID to run record |
| `scores` | object | no | Scoring summary keyed by run ID |
| `statistical_test` | string | no | Pre-registered statistical test name |
| `conclusion` | string | no | Result summary |
| `pre_acknowledged_limitations` | array | no | Limitations stated before analysis |

### Run record schema

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `group` | string | no | `control` or `treatment` |
| `session_id` | string | no | Session identifier from the run harness |
| `messages` | integer | no | Message count in the session |
| `input_tokens` | integer | no | Accumulated input tokens |
| `output_tokens` | integer | no | Accumulated output tokens |
| `total_tokens` | integer | no | Sum of input and output tokens |
| `wall_clock_seconds` | number | no | Elapsed wall-clock seconds |
| `bytes` | integer \| null | yes | Session byte size, if recorded |
| `note` | string \| null | yes | Optional note (e.g. failure reason) |

## scores.json

Free-form per-criterion scoring keyed by run ID; each entry SHOULD include the score value, per-criterion results, and scorer justifications.

## v2.0 discrimination phase artifacts

The v2.0 phase (see [preregistration-v2.0.md](preregistration-v2.0.md)) uses the following artifacts. The frozen problem set, oracle, raw records, call log, and the committed endpoint numbers are immutable; documentation derives around them.

### problems-v2.json

| Field | Description |
|-------|-------------|
| `seed` | Generator PRNG seed (20260214) |
| `problems` | Array of 120 problems in committed order, each with `problem_id`, state (objective, constraints, candidates) |
| `pass2_order` | Committed permutation of problem ids for pass 2 |

### oracle-v2.json

Map of `problem_id` to analysis-side oracle values: `optimal_id` (feasible argmax), `decoy_id` (infeasible super-optimal candidate), and `stratum` (`S1`, `S2`, or `S3` by relative optimality gap).

### results/raw/v2/run-NNN.json (runs 001-240)

| Field | Type | Description |
|-------|------|-------------|
| `run` | integer | Call number 1-240 |
| `pass` | integer | 1 or 2 |
| `problem_id` | string | Frozen problem id |
| `timestamp` | string | ISO 8601 with UTC offset |
| `http_status` | integer | HTTP status of the judge call |
| `request` | object | Verbatim request: judge `state`, question, and per-option criteria |
| `response` | object | Verbatim response, including `model` (`jev-1.13.0`) and `answers.selection` with `choice` and per-option `probabilities` |
| `fallback` | boolean | Always false; the runner refuses fallback calls |

### results/calls-v2.jsonl

Append-only call log, one JSON object per line: `stage`, `run`, `model`, `fallback`, `noul`, `pass`, `problem_id`.

### experiments/judge-enumeration-v2/endpoints.json

Preregistered endpoints (frozen section (e) values, computed by `analyze_v2.py` with exact Fraction arithmetic):

| Field | Description |
|-------|-------------|
| `chance_rate` | 0.2 (1/5 menu options) |
| `primary.S1/S2/S3` | Per-stratum `n`, `agreements`, `agreement_rate`, `wilson95_low`, `wilson95_high` (both-call agreement, sealed criterion section (d)) |
| `primary.fisher_exact_S1_vs_S3_two_sided_p` | Pre-specified two-sided Fisher exact test |
| `primary.overall` | Overall agreement over n=120 problems |
| `secondary.prune_failure_*` | Selected id equals the decoy, overall and per stratum |
| `secondary.per_problem_disagreement` | Calls 1 and 2 disagree per problem |
| `secondary.brier_selected_probability` | Brier score on the selected-option probability |
| `secondary.ece_5_equal_width_bins` | Expected calibration error |
| `secondary.position_bias_over_menu_positions` | Agreement and prune failure by optimal-candidate position 1-5 |
| `exploratory` | Labeled exploratory analyses (per-call agreement) |
| `per_call` | Per-call records: run, pass, problem_id, stratum, selected_id, selected_prob, agreement, prune_failure |
