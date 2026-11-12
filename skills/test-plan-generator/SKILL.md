---
name: test-plan-generator
description: >-
  Writes a manual test plan from a source document: either regression coverage for an existing
  feature from its user-facing docs, or new-feature coverage from a product brief, spec or issue.
  Produces fixed-section Markdown tables with blank result columns, a regression-surface grade and
  exploratory-testing flags. Use when the user asks for a test plan, regression test plan, test
  cases for a feature, "what should I test for X", or hands over a README, spec or brief and asks
  how to QA it.
---

# Test Plan Generator

The model reads the source and writes the rows. Everything else is fixed: the input gate, the section
order, the columns, the allowed result values, the closure rows and the surface grading. Don't improvise those.

## Inputs

| Input | Required | Notes |
|---|---|---|
| Mode | yes | `regression` (existing feature) or `new-feature` |
| Feature name | yes | Scope of the plan; one feature, not a whole product |
| Source | yes | File path, URL or pasted text: user docs/README for `regression`; brief, spec, issue or design notes for `new-feature` |
| Environments | no | Result columns, e.g. `API, Browser`. Default: one per client surface the source describes |
| Reason for change | no | `regression` only; shown in the header |
| Known risks | no | Steers the Regression risk areas section; never a source of expected results |

If any required input is missing, ask for it in one message before reading further.

## Outputs

One Markdown plan shaped like [templates/plan.md](templates/plan.md), printed in chat. Write it to a
file only if the user gives a path. If the input gate fails, print the "Input incomplete" block from
the same template instead and stop.

## Procedure

### A. Gate (deterministic)

1. Read the whole source. For the chosen mode, tick each field below as **found** (quote where)
   or **missing**:
   - `regression`: feature name; user actions; observable outcomes of those actions; options or
     settings; contexts where it's supported; limits or constraints.
   - `new-feature`: feature name; user flows (main and alternative); states (empty, loading,
     populated, error, disabled); interaction behaviour; layout across screen sizes (UI only);
     options or settings; edge cases; acceptance criteria (optional, but recorded either way).
2. If any non-optional field is missing, emit "Input incomplete" listing each missing field and
   what would satisfy it. Don't produce a partial plan.

### B. Extract (deterministic)

3. Build three lists from the source, each item tagged with its location (heading, table row or line):
   **actions** (every documented operation), **options** (every setting, parameter or variant,
   with its default if stated), **contexts** (every surface, runtime, page or client it's said to
   work in). For `new-feature`, also number the acceptance criteria `AC-1`, `AC-2`, and so on.
4. Fix the result columns: the Environments input, or the client surfaces named in the source.

### C. Write rows (model)

5. Fill the sections in the template's order for the mode. Each section's purpose:
   - **Smoke checks**: 3 to 5 rows proving the feature is reachable and basically works.
   - **Core behaviour**: one row per item in the actions list, and its default state.
   - **Options and settings**: each option applied, reverted to default, and any pair the source
     says interacts.
   - **Regression risk areas** (`regression` only): behaviour shared with other features,
     effects that cascade from parent records or settings, and variants. Notes says which
     regression the row guards against.
   - **Edge cases and resilience**: limits and constraints from the source, then standard probes
     (empty, maximum, invalid format, repeated rapid action, reload after save, dependency down)
     only where the feature has the matching input or dependency.
   - **Contexts**: one row per item in the contexts list, with no expected result needed. Don't
     repeat core cases here.
   - **Accessibility and quality** (UI features only): labels, focus order, keyboard-only use,
     console errors on load.
6. Set environment cells using the rules in the template. Generated cells hold only `N/A` or stay blank.
7. Append the fixed closure rows from the template, unchanged.

### D. Assess and check (deterministic)

8. **Regression surface** (`regression` only): count the contexts list and grade it: 1 to 3 is
   Standard, 4 to 8 is Elevated, 9 or more is High. If Elevated or High, list every context and
   confirm it has a Contexts row.
9. **Acceptance criteria coverage** (`new-feature` only): map each `AC-n` to the row numbers that
   cover it. Mark any criterion that can't be observed as untestable and say why.
10. **Exploratory testing**: one bullet per area where rows aren't enough: behaviour the source
    leaves open, interacting states, timing or animation, third-party or user-generated content.
    State what to explore and what the source leaves unsaid.
11. Before emitting, verify each of these and fix any failure:
    - every row has a Source pointing into step 3's lists;
    - no row is duplicated;
    - the Smoke checks section has 3 to 5 rows;
    - every action has a Core row;
    - every context has a Contexts row;
    - result cells contain only `N/A` or blank.

## Rules

1. Every row cites a Source location in the input. If a row has no Source, drop it.
2. Never invent requirements. If the source doesn't state the expected result, write
   `Not stated: confirm with owner` in Expected and `Assumption` in Notes.
3. Results are never filled in. Generated cells are `N/A` or blank, and the plan title says Draft.
4. One action per row. Test case text starts with "User" (closure rows excepted). Expected
   describes what the user or client observes (screen, HTTP status, body), never internal state.
5. No duplicates across sections. A behaviour is tested once in Core and only its context is
   varied in Contexts.
6. Don't diagnose causes or propose implementation; flag gaps as questions instead.
7. Known risks steer where to add rows. They never supply expected results.
8. Emit only the template's sections, with no preamble or sign-off.

## Limitations

- The original read hosted help-centre guides and design files. Here the source must be readable
  text: a file, a reachable URL or pasted content. Design tools aren't read directly.
- The original's section set and rules were tied to a specific page-builder product (sections, block
  toolbars, template versions, plan tiers). They're replaced with generic sections.
- The original's per-block playbook mode depended on an internal master plan and incident history.
  It's dropped.
- The original's interactive prompt-filling script is replaced by the skill asking for missing inputs.
- Spreadsheet export is replaced by Markdown tables. Results are recorded outside this skill.
- It plans testing; it doesn't execute tests or read results.
