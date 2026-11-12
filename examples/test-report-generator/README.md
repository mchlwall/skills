# test-report-generator example

## Input

[`examples/test-plan-generator/test-report.md`](../test-plan-generator/test-report.md): the regression plan test-plan-generator produced for the project-manager Tasks feature. It hasn't been executed, so every result cell is blank or `N/A`. An excerpt:

```
## Core behaviour

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 4 | User adds a task to a project with only a title | Task is created with status `TODO` and priority `MEDIUM` | | | | `README.md:76`, `README.md:85-86` |
| 5 | User adds a task with title, description, priority `HIGH` and due date `2026-12-01` | Task is created with exactly those values | | N/A | UI fields for description, priority and due date not described in source | `README.md:76`, `README.md:84-87` |
| 6 | User lists a project's tasks | Every task belonging to that project is returned, and no others | | | | `README.md:77` |
| 7 | User gets one task by id | The task is returned with `id`, `projectId`, `title`, ... | | N/A | | `README.md:78`, `README.md:84-87` |
```

## What I changed

- Nothing yet. [test-report.md](test-report.md) is the script's output exactly as generated, before review.

## How to reproduce

From the repo root:

```bash
python3 skills/test-report-generator/scripts/summarise_plan.py \
  --input examples/test-plan-generator/test-report.md \
  --context "project-manager e738e6f; plan generated, not yet executed" \
  --output examples/test-report-generator/test-report.md
```

Or prompt: `Use the test-report-generator skill to summarise examples/test-plan-generator/test-report.md.`
