"""Validation script for Deal Intelligence Agent deals dataset.

Verifies conformance to CONTRACT.md specifications and data quality rules:
- File existence and valid JSON parsing
- Required deal fields (id, company, value, outcome, calls)
- Deal ID uniqueness
- Outcome values in ('won', 'lost', None) with required 2 won, 2 lost, 2 open distribution
- Deal values are numeric and within $40k - $400k range
- Calls have ascending call_no starting from 1
- Required call fields (call_no, date, participants, transcript)
- ISO format dates (YYYY-MM-DD)
- Non-empty participants list
- Non-empty transcripts with realistic length (150 - 300 words)
- Demo deal verification (Northwind Logistics has calls 1-4 in deals.json, and Call 5 in demo_call_5.json)
"""

import json
from pathlib import Path
import re
import sys

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def count_words(text: str) -> int:
    """Return count of words in text, ignoring whitespace."""
    return len(text.strip().split())


def validate_call(call: dict, deal_id: str, expected_call_no: int) -> list[str]:
    """Validate a single call dictionary."""
    errors = []
    required_fields = ["call_no", "date", "participants", "transcript"]

    for field in required_fields:
        if field not in call:
            errors.append(f"[{deal_id}] Call is missing required field '{field}'")

    call_no = call.get("call_no")
    if call_no != expected_call_no:
        errors.append(
            f"[{deal_id}] Expected call_no {expected_call_no}, found {call_no}"
        )

    date_str = call.get("date", "")
    if not isinstance(date_str, str) or not DATE_REGEX.match(date_str):
        errors.append(
            f"[{deal_id}] Call {call_no} has invalid date format '{date_str}' (expected YYYY-MM-DD)"
        )

    participants = call.get("participants", [])
    if not isinstance(participants, list) or len(participants) == 0:
        errors.append(
            f"[{deal_id}] Call {call_no} participants must be a non-empty list"
        )
    else:
        for p in participants:
            if not isinstance(p, str) or not p.strip():
                errors.append(
                    f"[{deal_id}] Call {call_no} contains invalid empty participant name"
                )

    transcript = call.get("transcript", "")
    if not isinstance(transcript, str) or not transcript.strip():
        errors.append(f"[{deal_id}] Call {call_no} transcript is empty")
    else:
        words = count_words(transcript)
        if words < 150 or words > 300:
            errors.append(
                f"[{deal_id}] Call {call_no} transcript word count {words} outside 150-300 range"
            )

    return errors


def validate_deals_file(deals_path: Path) -> tuple[bool, list[str], dict]:
    """Validate data/deals.json file against CONTRACT.md."""
    errors = []
    stats = {
        "deals_count": 0,
        "total_calls": 0,
        "outcomes": {"won": 0, "lost": 0, "open": 0},
        "deals_summary": [],
    }

    if not deals_path.exists():
        return False, [f"File not found: {deals_path}"], stats

    try:
        data = json.loads(deals_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"Failed to parse JSON from {deals_path}: {exc}"], stats

    if not isinstance(data, list):
        return False, ["Root JSON must be a list of deals"], stats

    stats["deals_count"] = len(data)
    seen_ids = set()

    for idx, deal in enumerate(data):
        deal_id = deal.get("id") or deal.get("deal_id")
        if not deal_id:
            errors.append(f"Deal index {idx} missing 'id' or 'deal_id'")
            deal_id = f"unknown-{idx}"
        elif deal_id in seen_ids:
            errors.append(f"Duplicate deal id: '{deal_id}'")
        seen_ids.add(deal_id)

        company = deal.get("company", "").strip()
        if not company:
            errors.append(f"[{deal_id}] Missing or empty 'company'")

        value = deal.get("value")
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"[{deal_id}] 'value' must be a positive number, got {value}")
        elif value < 40000 or value > 400000:
            errors.append(
                f"[{deal_id}] 'value' ${value:,.0f} outside expected range $40k - $400k"
            )

        outcome = deal.get("outcome")
        if outcome not in ("won", "lost", None):
            errors.append(
                f"[{deal_id}] 'outcome' must be 'won', 'lost', or null (got '{outcome}')"
            )
        else:
            outcome_key = outcome if outcome else "open"
            stats["outcomes"][outcome_key] += 1

        calls = deal.get("calls", [])
        if not isinstance(calls, list) or len(calls) == 0:
            errors.append(f"[{deal_id}] 'calls' must be a non-empty list")
        else:
            stats["total_calls"] += len(calls)
            for c_idx, call in enumerate(calls, start=1):
                call_errors = validate_call(call, deal_id, expected_call_no=c_idx)
                errors.extend(call_errors)

        stats["deals_summary"].append(
            {
                "id": deal_id,
                "company": company,
                "value": value,
                "outcome": outcome or "open",
                "calls_count": len(calls) if isinstance(calls, list) else 0,
            }
        )

    # Validate distribution: 6 deals, 2 won, 2 lost, 2 open
    if len(data) != 6:
        errors.append(f"Expected exactly 6 deals, found {len(data)}")

    if stats["outcomes"]["won"] != 2:
        errors.append(f"Expected 2 won deals, found {stats['outcomes']['won']}")
    if stats["outcomes"]["lost"] != 2:
        errors.append(f"Expected 2 lost deals, found {stats['outcomes']['lost']}")
    if stats["outcomes"]["open"] != 2:
        errors.append(f"Expected 2 open deals, found {stats['outcomes']['open']}")

    return len(errors) == 0, errors, stats


def validate_demo_call(demo_path: Path) -> tuple[bool, list[str]]:
    """Validate data/demo_call_5.json for the live demo."""
    errors = []
    if not demo_path.exists():
        return False, [f"Demo call file not found: {demo_path}"]

    try:
        call = json.loads(demo_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"Failed to parse JSON from {demo_path}: {exc}"]

    if not isinstance(call, dict):
        return False, ["data/demo_call_5.json must be a single call JSON object"]

    call_errors = validate_call(call, "demo_call_5", expected_call_no=5)
    errors.extend(call_errors)

    return len(errors) == 0, errors


def main():
    base_dir = Path(__file__).resolve().parent
    deals_file = base_dir / "deals.json"
    demo_file = base_dir / "demo_call_5.json"

    print("=" * 60)
    print("DEAL INTELLIGENCE AGENT - DATASET VALIDATION")
    print("=" * 60)
    print(f"Checking deals file: {deals_file}")
    deals_valid, deals_errors, stats = validate_deals_file(deals_file)

    print(f"Checking demo call:  {demo_file}")
    demo_valid, demo_errors = validate_demo_call(demo_file)

    all_errors = deals_errors + demo_errors

    print("-" * 60)
    print("DATASET METRICS & SUMMARY:")
    print(f"  Total Deals:       {stats['deals_count']}")
    print(f"  Total Calls:       {stats['total_calls']}")
    print(
        f"  Outcome Breakdown: Won={stats['outcomes']['won']} | Lost={stats['outcomes']['lost']} | Open={stats['outcomes']['open']}"
    )
    print("\nDEAL ROSTER:")
    for d in stats.get("deals_summary", []):
        print(
            f"  * {d['id']:<8} | {d['company']:<26} | ${d['value']:>8,f} | {d['outcome']:<6} | {d['calls_count']} calls"
        )

    # Check demo deal specifics
    northwind = next(
        (d for d in stats.get("deals_summary", []) if d["company"] == "Northwind Logistics"),
        None,
    )
    if northwind:
        print(
            f"\nDEMO DEAL STATUS: Found '{northwind['company']}' with {northwind['calls_count']} calls in deals.json (Call 5 in demo_call_5.json)"
        )
    else:
        all_errors.append("Demo deal 'Northwind Logistics' was not found in deals.json")

    print("-" * 60)
    if all_errors:
        print("[FAIL] VALIDATION FAILED with errors:")
        for err in all_errors:
            print(f"  - {err}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("[OK] ALL CHECKS PASSED: Dataset strictly conforms to CONTRACT.md")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
