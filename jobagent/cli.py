"""Run a safe demo or (when privately configured) a read-only production scan."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .config import ConfigurationError, load_demo_profile, load_private_profile, load_private_sources
from .pipeline import assemble, scan
from .transport import send_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="open-job-agent")
    parser.add_argument("mode", choices=["demo", "scan", "test-webhook"],
                        help="demo: synthetic offline data | scan: approved public board APIs | test-webhook: signed empty payload")
    parser.add_argument("--send", action="store_true", help="Send signed report to your privately configured Sheets web app")
    parser.add_argument("--output", default="build/report.json", help="Ignored, local result file")
    args = parser.parse_args(argv)
    try:
        if args.mode == "demo":
            sample = Path(__file__).resolve().parents[1] / "data/sample_jobs.json"
            jobs = json.loads(sample.read_text(encoding="utf-8"))
            report = assemble(jobs, load_demo_profile(), "synthetic_demo")
        elif args.mode == "test-webhook":
            report = {"schema_version": 1, "source": "connectivity_test", "jobs": [],
                      "stats": {"seen": 0, "deduplicated": 0, "reported": 0, "review": 0, "errors": 0}}
        else:
            report = scan(load_private_sources(), load_private_profile())
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        # No job titles, candidate details, endpoints, API keys, or payloads in CI logs.
        print("RESULT: " + json.dumps(report["stats"], sort_keys=True))
        if args.send:
            ack = send_report(report)
            print("SYNC: " + json.dumps(ack, sort_keys=True))
        else:
            print("SYNC: skipped (local mode)")
        return 0
    except (ConfigurationError, ValueError, RuntimeError) as exc:
        # Exceptions from config carry only labels, never original secret values.
        print("ERROR: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
