# Plan template

Fill the `<placeholders>`. Keep the section order and column order exactly as written. Number rows
continuously across all sections so notes can refer to `#12`.

## Columns

Every section table uses the same columns. Write one result column per environment, in the order fixed in step 4:

| # | Test case | Expected | <Env 1> | <Env 2> | Notes | Source |
|---|---|---|---|---|---|---|

Allowed result values: `Pass`, `Fail`, `Blocked`, `N/A` and blank. The generator only writes `N/A` or leaves the cell blank.
Testers record failures in Notes as `<issue-id>: <short description>`, and blocked rows as `Blocked by #<row>`.

## Environment cell rules

Mark an environment `N/A` when:

- the source doesn't describe the action on that surface (for example, a raw HTTP parameter with no UI control);
- the row is a context row for a different surface.

Leave the cell blank, meaning the row should be run there, when:

- the action exists on that surface;
- the row covers shared behaviour every surface depends on: stored data, defaults, error messages, deletes that cascade to child records.

## Regression plan

```markdown
# Test plan (Draft): <feature> (regression)

- **Source:** <file, URL or "pasted text"> (<sections used>)
- **Reason for change:** <reason or "not given">
- **Environments:** <Env 1>, <Env 2>

## Smoke checks
<table>

## Core behaviour
<table>

## Options and settings
<table>

## Regression risk areas
<table>

## Edge cases and resilience
<table>

## Contexts
<table>

## Accessibility and quality
<table, or leave the section out if the feature has no UI>

## Closure
<closure rows>

## Regression surface

| Contexts counted | Grade | Action |
|---|---|---|
| <n>: <list> | <Standard / Elevated / High> | <Standard: plan as written / Elevated: every context has its own row (confirmed) / High: review with team, split into per-context passes> |

## Exploratory testing
- **<area>:** <what to explore>. <what the source leaves unsaid>.
```

## New-feature plan

The new-feature plan has the same header, minus Reason for change. Its sections, in order:

1. Smoke checks
2. Core behaviour
3. Options and settings
4. Edge cases and resilience
5. Accessibility and quality
6. Contexts
7. Closure

After the sections:

```markdown
## Acceptance criteria coverage

| Criterion | Rows | Note |
|---|---|---|
| AC-1: <criterion> | #4, #9 | <blank, or "Untestable: <why>"> |

## Exploratory testing
- **<area>:** <what to explore>. <what the source leaves unsaid>.
```

## Closure rows

Append these four rows at the end, word for word, with Expected, results, Notes and Source blank:

| # | Test case | Expected | <Env 1> | <Env 2> | Notes | Source |
|---|---|---|---|---|---|---|
| <n> | Time-boxed exploratory session | | | | | |
| <n+1> | Element and layout check | | | | | |
| <n+2> | Accessibility check | | | | | |
| <n+3> | Localisation check | | | | | |

## Input incomplete

```markdown
# Test plan (not generated): <feature>

| Field | Status | What would satisfy it |
|---|---|---|
| <field> | Missing | <what to add to the source> |
| <field> | Found | <quote location> |

Add the missing information to the source, or paste it here, and run again.
```
