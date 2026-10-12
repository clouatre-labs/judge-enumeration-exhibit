"""Run the sealed judge protocol against the frozen enumeration state.

Reads frozen_state.json, posts the preregistered question to the
typesafe systemone endpoint with the pinned model jev-1.13.0, and
records the full request and response verbatim for each call
(default 5 sequential calls; see --runs and --start).

Retry/fallback note: the fallback envelope handling below is a
documented reimplementation of the SDK's fallback envelope semantics
({"fallback": true, "error": ...}); a fallback response is recorded
and counted, never silently skipped, and the script exits non-zero if
any call falls back.

Usage:
    python3 run_judge.py             # run 5 calls (requires TYPESAFE_API_KEY)
    python3 run_judge.py --runs 55 --start 6  # preregistered v1.1.0 extension
    python3 run_judge.py --dry-run   # validate inputs, print one request body, send nothing
    python3 run_judge.py --help
"""

import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

JUDGE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"  # strict allowlist: the only URL ever passed to urlopen
MODEL = "jev-1.13.0"
N_RUNS = 5

INSTRUCTIONS = (
    "Which candidate production plan should be selected for this "
    "blending decision?"
)


def criterion_text(objective, x, cid):
    """Preregistered per-option criterion text (see preregistration.md)."""
    x1, x2, x3 = x
    return (
        "Select the plan with objective value %g at production levels "
        "x=(%g, %g, %g) (candidate %s)" % (objective, x1, x2, x3, cid)
    )


def load_state(path):
    with open(path) as f:
        return json.load(f)


def build_request_body(state):
    """Build the request body; must match preregistration.md verbatim."""
    criteria = {
        c["id"]: criterion_text(c["objective"], c["x"], c["id"])
        for c in state["candidates"]
    }
    return {
        "state": state,
        "questions": {
            "selection": {
                "type": "choice",
                "instructions": INSTRUCTIONS,
                "criteria": criteria,
            }
        },
        "model": MODEL,
    }


def call_judge(body, api_key):
    """POST the request; returns (parsed_response, http_status, fallback)."""
    # SSRF allowlist: only the fixed module-level endpoint is ever requested.
    parsed_url = urllib.parse.urlsplit(JUDGE_ENDPOINT)
    if parsed_url.scheme != "https" or parsed_url.netloc != "api.typesafe.ai":
        raise ValueError(
            "refusing non-allowlisted judge endpoint: %r" % JUDGE_ENDPOINT
        )
    data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                JUDGE_ENDPOINT,
                data=data,
                headers={
                    "Authorization": "Bearer %s" % api_key,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                method="POST",
            ),
            timeout=30,
        ) as resp:
            text = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = {"raw": text}
    fallback = bool(parsed.get("fallback")) or "error" in parsed
    return parsed, status, fallback


def main():
    parser = argparse.ArgumentParser(
        description="Sealed judge runner for the enumeration exhibit."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate inputs and print the request body without sending",
    )
    parser.add_argument(
        "--state",
        default="frozen_state.json",
        help="path to the frozen state JSON (default: frozen_state.json)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=N_RUNS,
        help="number of sequential calls (default: %d)" % N_RUNS,
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="run number of the first call (default: 1); later runs append "
        "to the raw directory and call log",
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="output directory for raw records and the call log",
    )
    args = parser.parse_args()

    state = load_state(args.state)
    body = build_request_body(state)

    if args.dry_run:
        json.dump(body, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("error: TYPESAFE_API_KEY is not set", file=sys.stderr)
        return 2

    results = pathlib.Path(args.results_dir)
    raw_dir = results / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    log_path = results / "calls.jsonl"

    any_fallback = False
    for run in range(args.start, args.start + args.runs):
        raw_path = raw_dir / ("run-%02d.json" % run)
        if raw_path.exists():
            print(
                "error: refusing to overwrite existing record %s" % raw_path,
                file=sys.stderr,
            )
            return 3
        parsed, status, fallback = call_judge(body, api_key)
        any_fallback = any_fallback or fallback
        record = {
            "stage": "judge",
            "run": run,
            "model": MODEL,
            "fallback": fallback,
            "noul": None,
        }
        with open(log_path, "a") as log:
            log.write(json.dumps(record) + "\n")
        raw = {
            "run": run,
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(timespec="seconds"),
            "http_status": status,
            "request": body,
            "response": parsed,
        }
        with open(raw_path, "w") as f:
            json.dump(raw, f, indent=2)
            f.write("\n")
        print(
            "run %d: status=%d fallback=%s"
            % (run, status, fallback)
        )

    if any_fallback:
        print("error: at least one judge call fell back", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
