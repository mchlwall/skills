---
name: regression-analyzer
description: >-
  Reads a branch diff and turns it into a short regression plan: risk-weighted manual test cases,
  each traced to a changed line, plus the smallest set of existing automated suites worth running,
  with a run command for each. Use when the user asks for a regression analysis, regression risk,
  "what should I test for this branch/PR", "which suites should I run for this change", a QA pass
  over a diff, or test cases for a merged pull request.
---

# Regression Analyzer

Git and shell do the counting, filtering and lookups. The model is only used to judge what
behaviour changed, how risky it is, and which checks would catch a regression.

## Inputs

| Input | Required | Default |
|---|---|---|
| Target repository path | yes | current workspace |
| Head ref | no | `HEAD` |
| Base ref | no | `git merge-base origin/main <head>`, else `main` |
| Change notes: what changed, areas touched, known risks | no (ask once) | none |
| `suite-mapping.md` anywhere in the repo | no | suite list read from `run-suite.sh` |

For an already-merged pull request, use `<merge-commit>^1` as base and the merge commit as head.
If base and head resolve to the same commit, report that there is nothing to analyse and stop.

## Outputs

A single Markdown report shaped like [templates/report.md](templates/report.md): a facts header,
a manual test case table, a suite table, and an optional flags list. If a gate fails, the report
uses the short "not run" variant from the same template instead. Nothing is written to the target repo.

## Procedure

### A. Collect facts (deterministic)

1. List the changes and totals:
   ```bash
   git -C "$REPO" diff --name-status "$BASE" "$HEAD"
   git -C "$REPO" diff --shortstat "$BASE" "$HEAD"
   ```
2. Load suites. If the repo has a `suite-mapping.md` (format: [templates/suite-mapping.md](templates/suite-mapping.md)),
   take the suite list, path rules and ignored paths from it. Otherwise:
   - suites = the labels in the `case` statement of `run-suite.sh`, leaving out the `*` fallback
     and any label that runs everything (such as `all`);
   - ignored paths = the defaults in step 3;
   - add a flag saying areas were judged because no mapping file exists.
3. Classify every changed file (first match wins):
   - **Ignored**: matches an ignored path. Defaults: test sources (`**/src/test/**`, `**/*Test.java`,
     `**/*.spec.*`, `**/*.test.*`), docs (`**/*.md`, `docs/**`), CI and tooling (`.github/**`,
     `**/scripts/**`, lint and formatter config). Ignored files never get test cases.
   - **Mapped**: matches a path rule. Record its area, suites and risk floor.
   - **Unmapped**: anything else. Its area is decided in step 8.
4. **Size gate**: more than 30 mapped plus unmapped files means you emit the "not run" variant and stop.
   If every file is ignored, emit the report with an empty case table, mark the highest risk as Low, and stop.
5. Detect PR CI coverage. Read `.github/workflows/*.yml` with a `pull_request` trigger. A suite
   counts as **Yes** if a step runs it by name (`run-suite.sh <suite>`, `-Dgroups=<suite>`, a tag
   filter) or runs the test module that contains it with no filter at all. Otherwise it counts as **No**.
   Record the workflow file and job name.
6. Read the hunks for every mapped or unmapped file: `git -C "$REPO" diff -U5 "$BASE" "$HEAD" -- <file>`.
   Note the new-side line numbers, because cases cite them.

### B. Judge (model)

7. For each file, state in one line what behaviour changed. Formatting, whitespace or a rename
   with no effect on logic counts as cosmetic and gets no cases. If you can't tell what changed,
   record an ambiguity flag naming the file and the question that would settle it.
8. Give each unmapped file an area. Reuse an area from the mapping or a suite name where one fits;
   otherwise name the area after its top-level package or directory and flag it.
9. **Area gate**: if the changes span more than 3 unrelated areas, emit the "not run" variant and stop.
10. Rate each change using [Risk levels](#risk-levels). Start from the path rule's floor (Low if
    there is none) and raise it when the content warrants. Never go below the floor. Code reached
    from more than one area takes the highest level among those areas.
11. Write the manual cases. Aim for 5 to 10. A narrow diff can have fewer; going over 10 needs a
    flag explaining why. Allocate cases by risk, giving High changes the most. Each case is one action a
    tester can perform and observe. Prefer regression checks on existing behaviour next to the change
    over re-testing the new behaviour alone.
12. Choose suites. Only pick a suite if one of its areas contains a mapped or unmapped file, and
    choose the narrowest that covers the change. If only some of a suite's tests exercise the change,
    give a class or method selector under "Narrow to"; otherwise write "Full suite". If you need more
    than 6 suites, emit the "not run" variant, since the change is too broad.

### C. Check and emit (deterministic)

13. Build each run command from `run-suite.sh`'s path and the suite name. Add a selector argument
    only when the script forwards extra arguments to the test runner (look for `"$@"`).
14. Before emitting, verify:
    - every suite name in the output appears in the list from step 2;
    - every Source cell names a file from step 1 and a line inside one of its hunks;
    - the case count is within 5 to 10, or the reason is flagged.
    Fix any failure, then fill the template.

## Risk levels

- **High**: sign-in and permissions; money movement; writes to persistent storage (schema,
  repositories, cascading deletes, migrations); shared code such as error handling, serialisation
  or utilities used by several areas.
- **Medium**: request validation and response shape; endpoints and routing; rendered UI;
  configuration and feature toggles; localisation.
- **Low**: copy-only text; styling confined to one component; test-only changes; docs and comments.

## Rules

1. Every manual case has at least one `file:line` Source from the diff. If you can't cite one, drop the case.
2. Copy suite names exactly from the suite list. Never invent, shorten or rename a suite.
3. Describe what changed and what could regress. Never claim a root cause, and never suggest code
   fixes, refactors or alternative designs.
4. Never add requirements. Expected behaviour must come from the diff or the change notes. If it
   can't, write "Confirm with author" and add an ambiguity flag.
5. Change notes help you decide where to look, but they don't replace the diff. Flag anything
   the notes claim that the diff doesn't show, and don't write cases for it.
6. No cases or suites for areas the diff doesn't touch.
7. Every case has Status `Draft`, and the report title says Draft. Only a human reviewer removes it.
8. Emit only the sections in the template. No preamble, summary or sign-off.

## Limitations

- The original workflow included deploying the branch to a shared test environment. There's no
  public equivalent, so this step is dropped. The skill neither starts the app nor runs suites.
- It doesn't read test results (`testRunSummary.json`, CI logs). It plans testing; it doesn't triage it.
- Without a `suite-mapping.md`, assigning files to areas is judgement and will vary between runs.
- PR CI detection only reads the workflow text. It can't see branch protection, so **Yes** means
  "the workflow runs it" and not "it's a required check".
- The original's cross-browser, device-grid and screen-reader suite families, and its
  product-specific risk categories, have no counterpart here and are left out.
- The original exported to a spreadsheet. This version emits Markdown tables instead.
- Performance, load and security testing are out of scope.
