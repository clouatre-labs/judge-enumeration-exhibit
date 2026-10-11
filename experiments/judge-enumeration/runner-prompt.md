# Runner Prompt: judge-enumeration

The runner is `run_judge.py` at the repository root. It is executed as:

```bash
TYPESAFE_API_KEY=<from environment> python3 run_judge.py
```

Runner instructions:

1. Load `frozen_state.json` (verify nothing changed since the
   preregistration commit).
2. Build the request body exactly as fixed in `run_judge.py`
   (`build_request_body`): the frozen state, one `choice` question
   named `selection` with the preregistered instructions and
   per-option criteria, and model `jev-1.13.0`.
3. Make 5 sequential POST calls to
   `https://api.typesafe.ai/v1/systemone` with a Bearer token taken
   from the environment (never hardcoded).
4. For each call, write the FULL request body and FULL response
   verbatim, plus an ISO 8601 timestamp with a +00:00 offset and the
   HTTP status, to `results/raw/run-0N.json`.
5. Append one call-log line per call (including fallback paths) to
   `results/calls.jsonl` as
   `{"stage":"judge","run":N,"model":"jev-1.13.0","fallback":<bool>,"noul":null}`.
6. Exit non-zero if any call falls back; a fallback envelope
   (`{"fallback": true, "error": ...}`) is recorded and counted,
   never silently skipped.
