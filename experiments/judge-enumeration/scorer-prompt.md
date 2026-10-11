# Scorer Prompt: judge-enumeration

Apply the sealed reading criterion from
[preregistration.md](../../preregistration.md) section (d), in full,
to each recorded raw response in `results/raw/run-0N.json`.

Per run N:

1. Read the selected option id from the raw response. Record it in
   `scores.json` under `treatment_N` as `selected_option`.
2. Agreement: mark `agrees_with_optimum` true if and only if the
   selected id is the M*=14480 candidate (candidate G,
   x=(9.2, 6, 4)).
3. After all five runs, compute consistency: the count of runs
   selecting the modal option. Record it once in `analysis.json`
   (`conclusion`).
4. Do not discard any run. A flat distribution (no modal option with
   at least 2 runs) is a reported finding, read as a question
   under-specification signal.
5. Both observed variance and observed stability are publishable
   outcomes ("stability, not quality"). n=5 bounds claims to
   variance/stability, not calibration.

Score blind: do not modify the preregistration, the frozen state, or
the raw responses while scoring.
