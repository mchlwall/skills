# Report template

Fill the `<placeholders>`. Keep the headings and column order exactly as written.

## Full report

```markdown
# Regression analysis (Draft)

- **Range:** `<base-sha-short>..<head-sha-short>` (<base-ref> to <head-ref>)
- **Files:** <total> changed: <production> analysed, <ignored> ignored
- **Areas:** <area> (<risk>), <area> (<risk>)
- **Highest risk:** <High | Medium | Low>
- **Suite source:** <path/to/suite-mapping.md | path/to/run-suite.sh (no mapping file)>

## 1. Manual test cases

| # | Test case | Expected behaviour | Risk | Source | Status |
|---|---|---|---|---|---|
| 1 | <one concrete action a tester performs> | <observable result, from the diff or notes> | <High/Medium/Low>: <what in this change could break it> | `<file>:<line>` | Draft |

## 2. Suite recommendations

| Suite | Why (tied to the diff) | Narrow to | Runs in PR CI | Run command |
|---|---|---|---|---|
| `<suite>` | <changed file or area it covers> | <Class or Class#method, or "Full suite"> | <Yes (<workflow> / <job>) or No> | `<run-suite.sh path> <suite> [selector]` |

## Flags

- Ambiguity: `<file>`: <what is unclear> (needs: <context that would resolve it>)
- Cosmetic only: `<file>`, `<file>`
- Area judged, not mapped: `<file>` assigned to <area>
- Notes not reflected in diff: <claim>
- More than 10 cases: <reason>
```

Rules for the full report:

- If no suite covers a changed area, the suite table has a single row: `None` | <reason> | n/a | n/a | n/a.
- If everything was ignored, the case table has a single row: `-` | No production changes | n/a | Low: test, docs or tooling only | n/a | Draft.
- Leave out the Flags heading when there are no flags. Leave out any flag line that has nothing to report.

## "Not run" variant (gate failed)

```markdown
# Regression analysis (not run)

- **Range:** `<base-sha-short>..<head-sha-short>`
- **Gate:** <size: N production files, limit 30 | areas: N unrelated areas, limit 3 | suites: N needed, limit 6>
- **Areas seen:** <area>, <area>, <area>

Split the change, or name the files or area to analyse, and run again.
```
