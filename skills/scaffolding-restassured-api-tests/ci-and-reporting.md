# CI and Reporting

previous tool runs on Drone with Bonfire/Ghost Story/Heliograph. A personal repo gets the same shape from GitHub Actions alone.

## Contents
- scripts/run-suite.sh
- scripts/run-stability-check.sh
- .github/workflows/api-tests.yml
- Starting the app under test
- testRunSummary.json format
- docs/triage-runbook.md outline

## scripts/run-suite.sh

```bash
#!/usr/bin/env bash
# Usage: ./scripts/run-suite.sh <suite-id|gradle-task>
# TESTS_BLOCKING (default: false) - when false, exit 0 even if tests fail
SUITE_OR_TASK="${1:?Usage: $0 <suite-id|gradle-task>}"

case "$SUITE_OR_TASK" in
  smoke)        TASK="testSmoke" ;;
  projects)     TASK="testProjects" ;;
  tasks)        TASK="testTasks" ;;
  unit)         TASK="testUnit" ;;
  all)          TASK="test" ;;
  *)            TASK="$SUITE_OR_TASK" ;;
esac

cd "$(dirname "${BASH_SOURCE[0]}")/.."
./gradlew clean "$TASK" --no-daemon --no-build-cache
RC=$?

if [ "${TESTS_BLOCKING:-false}" = "true" ]; then
  exit $RC
fi
exit 0
```

`--no-build-cache` stops Gradle replaying test results `FROM-CACHE` in CI.

## scripts/run-stability-check.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
# Usage:   ./scripts/run-stability-check.sh <test-target> [runs]
# Example: ./scripts/run-stability-check.sh apiTests.tasks.TasksTests.completeTask 10

TEST_TARGET="${1:?Usage: $0 <test-target> [runs]}"
RUNS="${2:-3}"
[[ "$RUNS" =~ ^[1-9][0-9]*$ ]] || { echo "runs must be a positive integer" >&2; exit 1; }

cd "$(dirname "${BASH_SOURCE[0]}")/.."

for i in $(seq 1 "$RUNS"); do
  echo "=== Run $i of $RUNS ==="
  if OUTPUT=$(./gradlew -q test --tests "$TEST_TARGET" --console=plain 2>&1); then
    echo "Run $i: PASSED"
  else
    echo "$OUTPUT" | tail -20
    echo "Stability check FAILED on run $i/$RUNS" >&2
    exit 1
  fi
done
echo "All $RUNS run(s) passed."
```

`chmod +x scripts/*.sh` once and commit the executable bit.

## .github/workflows/api-tests.yml

```yaml
name: API Tests

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 9-18 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  checks: write

concurrency:
  group: api-tests-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew spotlessCheck verifyTestTags testUnit --no-daemon

  suites:
    needs: verify
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        suite: [smoke, projects, tasks]
    env:
      BASE_URL: http://localhost:8080
      SUITE_TYPE: ${{ matrix.suite }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - uses: gradle/actions/setup-gradle@v4

      - name: Start app under test
        run: docker compose up -d

      - name: Wait for app health
        run: |
          for i in $(seq 1 30); do
            curl -fsS "$BASE_URL/health" && exit 0
            sleep 2
          done
          echo "App never became healthy" >&2
          docker compose logs
          exit 1

      - name: Run ${{ matrix.suite }} suite
        run: TESTS_BLOCKING=true ./scripts/run-suite.sh ${{ matrix.suite }}

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: report-${{ matrix.suite }}
          path: |
            build/reports/tests/
            build/test-results/
            build/artifacts/testRunSummary.json

      - name: Publish JUnit results
        if: always()
        uses: mikepenz/action-junit-report@v5
        with:
          report_paths: build/test-results/**/TEST-*.xml
          check_name: JUnit (${{ matrix.suite }})

      - name: Job summary
        if: always()
        run: |
          f=build/artifacts/testRunSummary.json
          if [ ! -f "$f" ]; then echo "No summary generated" >> "$GITHUB_STEP_SUMMARY"; exit 0; fi
          jq -r '"### 📋 \(.suiteType): \(.totals.tests) tests, \(.failedTests | length) failed",
                 (.failedTests[] | "- `\(.specPath)` :: \(.testName)\n  - Re-run: `\(.rerun)`")' \
            "$f" >> "$GITHUB_STEP_SUMMARY"

  report:
    needs: suites
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: report-*
          path: reports
      - name: Build unified index
        run: |
          {
            echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Project Tracker API Test Report</title>'
            echo '<style>body{font-family:system-ui,sans-serif;margin:2rem}ul{line-height:1.8}</style></head>'
            echo '<body><h1>📋 Project Tracker API Test Report</h1><ul>'
            for idx in reports/report-*/reports/tests/*/index.html; do
              [ -f "$idx" ] || continue
              rel="${idx#reports/}"
              name="$(basename "$(dirname "$idx")")"
              echo "<li><a href=\"$rel\">$name</a></li>"
            done
            echo '</ul></body></html>'
          } > reports/index.html
      - uses: actions/upload-artifact@v4
        with:
          name: unified-report
          path: reports/

  alert:
    needs: suites
    if: failure() && github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - name: Slack failure alert
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          RUN_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
          curl -sS -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Project Tracker API tests failed on ${GITHUB_REF_NAME}. Run: ${RUN_URL}\"}" \
            "$SLACK_WEBHOOK_URL"
```

Optional extras:
- **Hosted report**: on `main`, add `pages: write` + `id-token: write` permissions to the `report` job, then
  `actions/upload-pages-artifact@v3` with `path: reports` followed by `actions/deploy-pages@v4`.
- **PR template**: `.github/pull_request_template.md` with "Tests pass / stability check screenshot attached" and "Docs updated".

## Starting the app under test

Pick whichever matches how the app is built, and keep the health-wait step:
- **Docker Compose** (default above): `docker-compose.yml` at the repo root exposing port 8080.
- **Same repo, Gradle module**: `./gradlew :app:bootRun > app.log 2>&1 &` (Spring Boot) and `cat app.log` on failure.
- **Separate repo, published image**: `docker run -d -p 8080:8080 ghcr.io/<you>/project-tracker-app:latest`.
- **Already deployed**: drop the start/wait steps and set `BASE_URL: ${{ vars.BASE_URL }}`.

The `/health` endpoint is what the `smoke` suite and the wait loop both depend on, so build it first.

## testRunSummary.json format

Written by `generateTestRunSummary` to `build/artifacts/testRunSummary.json` after every `Test` task:

```json
{
  "suiteType": "tasks",
  "runId": "11873450123",
  "repo": "<you>/project-tracker-api-tests",
  "commit": "4f1c2e9",
  "isScheduled": false,
  "baseUrl": "http://localhost:8080",
  "totals": { "tests": 7, "failures": 1, "errors": 0, "skipped": 0 },
  "failedTests": [
    {
      "suite": "testTasks",
      "specPath": "apiTests.tasks.TasksTests",
      "testName": "completeTask()",
      "error": "Expected: is \"DONE\" but: was \"IN_PROGRESS\"",
      "rerun": "./gradlew test --tests \"apiTests.tasks.TasksTests\""
    }
  ]
}
```

It's the machine-readable hook for anything downstream: job summaries, Slack messages, a flaky-test
tracker, or a dashboard. `specPath` is directly usable with `--tests`.

## docs/triage-runbook.md outline

1. **Where alerts come from**: scheduled run failure → Slack message with run link.
2. **Find the report**: Actions run → job summary for the failed list → `unified-report` artifact for HTML
   (failed tests include request/response bodies from `ResponseLoggingExtension`).
3. **Re-run**: "Re-run failed jobs" in Actions, or locally with the `rerun` command from the summary.
4. **Common failures**: app not healthy (check `docker compose logs`), timeouts (raise `TestTimeouts` tier),
   data collisions between tests (make the test create its own data).
5. **Real bug**: open an issue with the failing request/response and the test name.
