# Report template

`scripts/summarise_plan.py` fills everything below the marker with Python `string.Template`
placeholders (`$name`). Edit the layout here; don't hand-fill the numbers. A literal dollar sign
must be written as `$$`.

<!-- report -->
# $title: test report

- **Verdict:** $verdict
- **Context:** $context
- **Source:** $total test rows ($closure closure rows excluded)

## Headline

| Metric | Value |
|---|---|
| Pass rate (passed ÷ executed) | $pass_rate |
| Executed (passed + failed) | $executed |
| Passed | $passed |
| Failed | $failed |
| Blocked | $blocked |
| Out of scope (all N/A) | $oos |
| Not run | $not_run |
| Expected result not confirmed in plan | $unconfirmed |

## By area

| Area | Cases | Passed | Failed | Blocked | Out of scope | Not run |
|---|---|---|---|---|---|---|
$section_rows

## By environment

| Environment | Pass | Fail | Blocked | N/A | Blank |
|---|---|---|---|---|---|
$env_rows

## Failures

$failures

## Blocked

$blocked_list

## Out of scope

$oos_list

## Unrecognised result values

$unrecognised

## One-line summary

$summary
