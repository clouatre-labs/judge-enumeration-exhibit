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
    python3 run_judge.py --problems problems-v2.json --pass-id 1 \
        --runs 120                   # preregistered v2.0 pass 1 (after merge to main)
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

V2_INSTRUCTIONS = (
    "Which candidate production plan should be selected for this "
    "production decision, given the stated constraints and objective?"
)


def criterion_text(objective, x, cid):
    """Preregistered per-option criterion text (see preregistration.md)."""
    x1, x2, x3 = x
    return (
        "Select the plan with objective value %g at production levels "
        "x=(%g, %g, %g) (candidate %s)" % (objective, x1, x2, x3, cid)
    )


def v2_criterion_text(x, cid):
    """Preregistered v2.0 per-option criterion (preregistration-v2.0.md)."""
    x1, x2, x3 = x
    return "Candidate %s: production levels x=(%g, %g, %g)." % (
        cid,
        x1,
        x2,
        x3,
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


def build_v2_request_body(problem):
    """Build the v2.0 request body; must match preregistration-v2.0.md
    verbatim. The state carries no objective values (schema superset of
    the v1.x frozen state)."""
    state = {
        "problem_id": problem["problem_id"],
        "stratum": problem["stratum"],
        "objective": problem["c"],
        "constraints": {"A": problem["A"], "b": problem["b"]},
        "candidates": problem["candidates"],
    }
    criteria = {
        c["id"]: v2_criterion_text(c["x"], c["id"])
        for c in problem["candidates"]
    }
    return {
        "state": state,
        "questions": {
            "selection": {
                "type": "choice",
                "instructions": V2_INSTRUCTIONS,
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
        default=None,
        help="number of sequential calls (default: %d in v1.x mode)" % N_RUNS,
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="run number of the first call (default: 1); later runs append "
        "to the raw directory and call log",
    )
    parser.add_argument(
        "--problems",
        default=None,
        help="path to the v2.0 problems JSON (problems-v2.json); enables "
        "per-problem mode and overrides --state",
    )
    parser.add_argument(
        "--pass-id",
        type=int,
        choices=(1, 2),
        default=1,
        help="v2.0 pass: 1 = committed order, 2 = committed pass2_order "
        "permutation (default: 1)",
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="output directory for raw records and the call log",
    )
    args = parser.parse_args()

    if args.problems:
        if args.runs is not None:
            print(
                "error: --runs is not valid with --problems; each pass "
                "covers every problem exactly once",
                file=sys.stderr,
            )
            return 2
        with open(args.problems) as f:
            doc = json.load(f)
        by_id = {p["problem_id"]: p for p in doc["problems"]}
        if args.pass_id == 2:
            order = doc["pass2_order"]
        else:
            order = [p["problem_id"] for p in doc["problems"]]
        calls = [(pid, build_v2_request_body(by_id[pid])) for pid in order]
        raw_dir = pathlib.Path(args.results_dir) / "raw" / "v2"
        log_path = pathlib.Path(args.results_dir) / "calls-v2.jsonl"
    else:
        state = load_state(args.state)
        calls = [(None, build_request_body(state))]
        calls = calls * (args.runs if args.runs is not None else N_RUNS)
        raw_dir = pathlib.Path(args.results_dir) / "raw"
        log_path = pathlib.Path(args.results_dir) / "calls.jsonl"

    if args.dry_run:
        json.dump(calls[0][1], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("error: TYPESAFE_API_KEY is not set", file=sys.stderr)
        return 2

    raw_dir.mkdir(parents=True, exist_ok=True)

    any_fallback = False
    for offset, (problem_id, body) in enumerate(calls):
        run = args.start + offset
        raw_path = raw_dir / (
            ("run-%03d.json" % run)
            if problem_id is not None
            else ("run-%02d.json" % run)
        )
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
        if problem_id is not None:
            record["pass"] = args.pass_id
            record["problem_id"] = problem_id
        with open(log_path, "a") as log:
            log.write(json.dumps(record) + "\n")
        raw = {
            "run": run,
            "pass": args.pass_id if problem_id is not None else None,
            "problem_id": problem_id,
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
            "run %d: status=%d fallback=%s" % (run, status, fallback)
        )

    if any_fallback:
        print("error: at least one judge call fell back", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
