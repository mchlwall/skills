#!/usr/bin/env python3
"""Summarise an executed Markdown test plan into a Markdown test report.

Usage: summarise_plan.py --input plan.md [--output report.md] [--title T] [--context C] [--json]
Standard library only. Layout comes from ../templates/report.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from string import Template

FIXED_COLUMNS = {"#", "test case", "expected", "notes", "source", "severity"}
CLOSURE_ROWS = {
    "time-boxed exploratory session",
    "element and layout check",
    "accessibility check",
    "localisation check",
}
UNCONFIRMED = "not stated: confirm with owner"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "report.md"


def normalise(value):
    v = value.strip().lower()
    if v == "":
        return "blank"
    if v in {"n/a", "na", "-", "—"}:
        return "na"
    for word in ("pass", "fail", "blocked"):
        if v == word or v.startswith(word + " "):
            return word
    return "other"


def row_status(results):
    values = list(results.values())
    if "fail" in values:
        return "fail"
    if "blocked" in values:
        return "blocked"
    if "pass" in values:
        return "pass"
    if values and all(v == "na" for v in values):
        return "out of scope"
    return "not run"


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text):
    title, section, header, rows, closure = "", "(no section)", None, [], 0
    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            section, header = line[3:].strip(), None
        elif not line.strip().startswith("|"):
            header = None
        elif header is None:
            cells = [c.lower() for c in split_row(line)]
            header = cells if "test case" in cells else []
        elif not header or re.fullmatch(r"[\s|:-]+", line):
            continue
        else:
            cells = split_row(line) + [""] * len(header)
            record = dict(zip(header, cells))
            name = record["test case"]
            if name.lower() in CLOSURE_ROWS:
                closure += 1
                continue
            envs = [h for h in header if h not in FIXED_COLUMNS]
            results = {e: normalise(record[e]) for e in envs}
            rows.append({
                "section": section,
                "id": record.get("#", ""),
                "test": name,
                "notes": record.get("notes", ""),
                "unconfirmed": record.get("expected", "").lower().startswith(UNCONFIRMED),
                "results": results,
                "raw": {e: record[e] for e in envs},
                "status": row_status(results),
            })
    if not rows:
        sys.exit("No table with a 'Test case' column found. Is this a Markdown test plan?")
    return title, rows, closure


def metrics(rows, closure):
    statuses = ["pass", "fail", "blocked", "out of scope", "not run"]
    count = {s: sum(r["status"] == s for r in rows) for s in statuses}
    executed = count["pass"] + count["fail"]
    envs = list(rows[0]["results"])
    by_env = {e: {v: sum(r["results"].get(e) == v for r in rows)
                  for v in ("pass", "fail", "blocked", "na", "blank", "other")} for e in envs}
    sections = {}
    for r in rows:
        sections.setdefault(r["section"], {s: 0 for s in statuses})[r["status"]] += 1
    if count["fail"]:
        verdict = "Failures present"
    elif count["blocked"] or count["not run"]:
        verdict = "In progress"
    else:
        verdict = "All passed"
    return {
        "total": len(rows), "closure_rows": closure, "count": count, "executed": executed,
        "pass_rate": f"{round(count['pass'] / executed * 100)}%" if executed else "n/a (nothing executed)",
        "verdict": verdict, "by_env": by_env, "sections": sections,
        "unconfirmed": sum(r["unconfirmed"] for r in rows),
        "unrecognised": [f"#{r['id']} {e}: `{v}`" for r in rows for e, v in r["raw"].items()
                         if r["results"][e] == "other"],
    }


def listing(rows, status):
    hits = [f"- #{r['id']} {r['test']} ({r['section']})" + (f": {r['notes']}" if r["notes"] else "")
            for r in rows if r["status"] == status]
    return "\n".join(hits) or "None."


def render(title, context, m, rows):
    c = m["count"]
    section_rows = "\n".join(
        f"| {name} | {sum(s.values())} | {s['pass']} | {s['fail']} | {s['blocked']} | {s['out of scope']} | {s['not run']} |"
        for name, s in m["sections"].items())
    env_rows = "\n".join(
        f"| {e} | {v['pass']} | {v['fail']} | {v['blocked']} | {v['na']} | {v['blank']} |"
        for e, v in m["by_env"].items())
    summary = (f"{c['pass']}/{m['executed']} executed cases passed across {len(m['sections'])} areas; "
               f"{c['fail']} failed, {c['blocked']} blocked, {c['not run']} not run. Verdict: {m['verdict']}.")
    return Template(TEMPLATE.read_text().split("<!-- report -->", 1)[1].strip()).substitute(
        title=title, context=context or "none given", verdict=m["verdict"], total=m["total"],
        closure=m["closure_rows"], executed=m["executed"], pass_rate=m["pass_rate"],
        passed=c["pass"], failed=c["fail"], blocked=c["blocked"], oos=c["out of scope"],
        not_run=c["not run"], unconfirmed=m["unconfirmed"], section_rows=section_rows,
        env_rows=env_rows, failures=listing(rows, "fail"), blocked_list=listing(rows, "blocked"),
        oos_list=listing(rows, "out of scope"),
        unrecognised="\n".join(f"- {u}" for u in m["unrecognised"]) or "None.", summary=summary,
    ) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--output")
    ap.add_argument("--title", default="")
    ap.add_argument("--context", default="")
    ap.add_argument("--json", action="store_true", help="also print metrics as JSON to stderr")
    args = ap.parse_args()
    plan_title, rows, closure = parse(Path(args.input).read_text(encoding="utf-8"))
    m = metrics(rows, closure)
    report = render(args.title or plan_title or "Test plan", args.context, m, rows)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.json:
        print(json.dumps(m, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
