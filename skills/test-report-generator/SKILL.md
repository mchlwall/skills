---
name: test-report-generator
description: >-
  Turns an executed (or partly executed) Markdown test plan into a short test report for developers
  and feature owners: verdict, pass rate, counts by area and environment, and lists of failures,
  blocked and out-of-scope cases. A script does all the counting. Use when the user asks to
  "summarise this test plan", "write a test report", "how much did we test", "give the dev a QA
  summary", or wants a PR-ready one-liner of test results. Not for writing test cases.
---

# Test Report Generator

This is the reverse of test-plan-generator: a plan goes in, a report comes out. Every number comes
from `scripts/summarise_plan.py`. The model's only jobs are to find the plan, supply a title and
one line of context, run the script, and relay the result.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Plan | yes | Markdown file in the test-plan-generator layout: `##` section headings, tables with a `Test case` column |
| Title | no | Defaults to the plan's `#` heading |
| Context | no | One line: build, environment or date range tested |
| Output path | no | Defaults to printing in chat |

Result columns are found by elimination: every column except `#`, `Test case`, `Expected`, `Notes`,
`Source` and `Severity` counts as an environment. Tables without a `Test case` column (such as a
surface grade or coverage table) are skipped.

## Outputs

A Markdown report shaped like [templates/report.md](templates/report.md), with a verdict, a headline
metrics table, per-area and per-environment tables, lists of failures, blocked, out-of-scope and
unrecognised values, and a one-line summary for a PR description. Add `--json` for the raw metrics.

## Procedure

1. Get the plan as a file. If it was pasted in chat, save it unchanged to a temporary file first.
2. Run:
   ```bash
   python3 <skill-dir>/scripts/summarise_plan.py --input <plan.md> \
     [--output <report.md>] [--title "<title>"] [--context "<one line>"]
   ```
3. If the script exits with "No table with a 'Test case' column", the input isn't a plan in the
   expected layout. Say so and stop. Don't reformat the plan to make it parse.
4. If **Executed** is 0, tell the user the plan hasn't been run, so the report shows status, not
   quality. Confirm that's what they want before sharing it.
5. Relay the verdict and the one-line summary. Point to the report, and call out each non-empty
   Failures, Blocked or Unrecognised list by row number. Don't repeat the tables in chat.

## How the script decides

Each result cell normalises to `pass`, `fail`, `blocked`, `na`, blank, or `other` (anything else,
reported in its own section). Each row then takes one status, in this order:

| Row status | Condition |
|---|---|
| Failed | any cell is `fail` |
| Blocked | any cell is `blocked` (and none failed) |
| Passed | any cell is `pass` (and none failed or blocked) |
| Out of scope | every cell is `na` |
| Not run | anything else, including all blank |

- **Pass rate** is passed ÷ (passed + failed). It reads "n/a" when nothing was executed.
- **Verdict**: any failure gives "Failures present". Otherwise any blocked or not-run row gives
  "In progress". Otherwise the verdict is "All passed".
- The four fixed closure rows from test-plan-generator are excluded and counted separately.
- Rows whose Expected starts "Not stated: confirm with owner" are counted as unconfirmed.

## Rules

1. Never count, recount or adjust numbers by hand. If a number looks wrong, report the suspected
   parsing problem rather than correcting it.
2. Never add findings, causes, severities or recommendations that aren't in the plan's own rows.
   Failure explanations come only from that row's Notes.
3. Never edit the plan or the generated report. To change the layout, edit the template.
4. A report built from a plan with no executed rows must be described as status-only, never as
   evidence the feature works.
5. Keep the chat message to the verdict, the summary line and the notable lists.

## Limitations

- The original read tab-separated spreadsheet exports with fixed browser columns and produced a
  styled HTML page. This version reads Markdown tables, detects environment columns by
  elimination, and outputs Markdown only.
- The original also scanned row text for feature-flag and rollback keywords tied to its own naming
  conventions. That's dropped.
- Cells containing a literal `|` will split the row. Escape them or remove them before running.
- It reports on one plan at a time. It doesn't read automated results (JUnit XML,
  `testRunSummary.json`) or compare runs.
