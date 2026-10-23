"""Validate local fixture integrity and render the human review packet."""

import argparse
from pathlib import Path

from professor_ai.evaluation.fixtures import (
    check_dataset,
    dataset_path,
    load_dataset,
    render_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "evals")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--require-reviewed", action="store_true")
    packet = parser.add_mutually_exclusive_group()
    packet.add_argument("--write-review-packet", action="store_true")
    packet.add_argument("--check-review-packet", action="store_true")
    args = parser.parse_args()
    report = check_dataset(args.root, require_reviewed=args.require_reviewed)
    if report.status != "invalid" and (args.write_review_packet or args.check_review_packet):
        try:
            expected = render_review(load_dataset(args.root))
            target = dataset_path(args.root.resolve(), "REVIEW.md")
            if args.write_review_packet:
                target.write_text(expected, encoding="utf-8")
            elif target.read_text(encoding="utf-8") != expected:
                raise ValueError("stale review packet; run --write-review-packet")
        except (OSError, ValueError, RuntimeError) as error:
            report.passed = False
            report.status = "invalid"
            report.errors.append(str(error))
    if args.as_json:
        print(report.model_dump_json())
    else:
        print(
            f"{report.status}: {report.case_count} cases, {report.document_count} documents, "
            f"{report.reviewed_case_count} recorded human approvals"
        )
        for error in report.errors:
            print(error)
        if report.status == "review_required":
            print("Unreviewed cases: " + ", ".join(report.unreviewed_case_ids))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
