# Suite mapping template

Optional. Save as `suite-mapping.md` anywhere in the target repo (for example `docs/suite-mapping.md`).
When it exists, the analyzer looks up areas, suites and risk floors here instead of judging them.
Keep the suite list in sync with `run-suite.sh`.

```markdown
# Suite mapping

## Suites

| Suite | Area | Covers |
|---|---|---|
| `<suite-id>` | <area name> | <endpoints, pages or behaviours the suite exercises> |

## Path rules

First match wins. Patterns are globs relative to the repo root.

| Path pattern | Area | Suites | Risk floor |
|---|---|---|---|
| `<glob>` | <area name> | `<suite-id>`, `<suite-id>` | <High / Medium / Low> |

## Ignored paths

- `<glob>`
```

Example rows for a small REST service with a projects resource:

| Path pattern | Area | Suites | Risk floor |
|---|---|---|---|
| `src/main/java/**/project/**` | Projects | `projects` | Medium |
| `src/main/resources/schema.sql` | Persistence | `projects` | High |
| `src/main/java/**/health/**` | Health | `smoke` | Low |
