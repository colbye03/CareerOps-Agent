"""The runnable product boundary: local workspaces, synthetic demo, auditable output."""
import argparse
from importlib.resources import files
from pathlib import Path
import json
import sys

from jsonschema import ValidationError

from .engine import run, tailor
from .models import load_json, starter, validate
from .storage import save, record_event

PERSONAS = ["data-cloud-architect", "technical-program-manager", "infrastructure-architect"]


def parser():
    p = argparse.ArgumentParser(description="Candidate-specific CareerOps decision support")
    p.add_argument("--workspace", type=Path, default=Path(".careerops"))
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a private local workspace from a synthetic persona")
    init.add_argument("--persona", choices=PERSONAS, default=PERSONAS[0])
    scan = commands.add_parser("run", help="Ingest JSON jobs and execute the pipeline")
    scan.add_argument("--jobs", type=Path)
    commands.add_parser("jobs", help="Show ranked results and funnel")
    explain = commands.add_parser("explain", help="Show score dimensions, evidence and gaps")
    explain.add_argument("job_id")
    resume = commands.add_parser("resume", help="Retrieve a grounded Markdown evidence draft")
    resume.add_argument("job_id")
    ledger = commands.add_parser("ledger", help="List or record application/ATS status events")
    ledger.add_argument("--job-id")
    ledger.add_argument("--status")
    ledger.add_argument("--source", default="user_confirmed")
    ledger.add_argument("--observed-at")
    ledger.add_argument("--events", type=Path, help="Import normalized communication/ATS event metadata")
    return p


def execute(args):
    w = args.workspace
    if args.command == "init":
        if w.exists():
            raise ValueError("Workspace already exists; choose a new --workspace")
        w.mkdir(parents=True, mode=0o700)
        (w / ".gitignore").write_text("*\n", encoding="utf-8")
        persona = starter("personas", args.persona)
        # Only known synthetic resources are copied; no personal context is consulted.
        save(w / "candidate.json", persona["profile"])
        save(w / "evidence.json", persona["evidence"])
        save(w / "jobs.json", starter("jobs", "demo"))
        save(w / "ledger.json", [])
        for path in files("careerops").joinpath("resources/role-packs").iterdir():
            save(w / "role-packs" / path.name, json.loads(path.read_text()))
        return {"workspace": str(w), "persona": args.persona, "next": "careerops run"}
    if not (w / "candidate.json").exists():
        raise ValueError("Run careerops init first")
    ledger = validate("application", load_json(w / "ledger.json"))
    if args.command == "run":
        profile = load_json(w / "candidate.json")
        report = run(load_json(args.jobs or w / "jobs.json"), profile, load_json(w / "evidence.json"),
                     {key: load_json(w / "role-packs" / f"{key}.json") for key in profile["role_packs"]}, ledger)
        save(w / "report.json", report)
        return report
    if args.command == "ledger":
        if args.events and (args.job_id or args.status):
            raise ValueError("Use --events or --job-id/--status, not both")
        if bool(args.job_id) != bool(args.status):
            raise ValueError("--job-id and --status are required together")
        events = load_json(args.events) if args.events else ([{"job_id": args.job_id, "status": args.status,
                  "source": args.source, "observed_at": args.observed_at}] if args.job_id else [])
        if not isinstance(events, list):
            raise ValueError("Events input must be a JSON array")
        for event in events:
            record_event(ledger, **event)
        if events:
            save(w / "ledger.json", ledger)
        return ledger
    report = load_json(w / "report.json")
    if args.command == "jobs":
        return {"funnel": report["funnel"], "jobs": [{"id": r["job"]["id"], "title": r["job"]["title"],
                "company": r["job"]["company"], "score": r["score"], "decision": r["decision"],
                "exclusion": r["exclusion"]} for r in report["results"]]}
    result = next((r for r in report["results"] if r["job"]["id"] == args.job_id), None)
    if result is None:
        raise ValueError("Unknown job ID; consult careerops jobs")
    if args.command == "explain":
        return result
    if result["exclusion"]:
        raise ValueError("Cannot tailor an excluded job")
    # Regenerate retrieval against current candidate data; a stale report cannot quote deleted evidence.
    profile = load_json(w / "candidate.json")
    fresh = run([{k: v for k, v in result["job"].items() if k != "id"}], profile,
                load_json(w / "evidence.json"),
                {key: load_json(w / "role-packs" / f"{key}.json") for key in profile["role_packs"]}, ledger)["results"][0]
    if fresh["exclusion"]:
        raise ValueError("Job is now excluded; run careerops run to refresh")
    target = w / "resumes" / f"{args.job_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(tailor(fresh), encoding="utf-8")
    return {"draft": str(target), "notice": "Evidence draft only; review facts before submission"}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        print(json.dumps(execute(args), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ValidationError) as error:
        print(f"careerops: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
