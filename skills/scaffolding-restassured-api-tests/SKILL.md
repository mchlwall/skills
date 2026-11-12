---
name: scaffolding-restassured-api-tests
description: >-
  Scaffolds and grows a small Java API test framework (RestAssured, JUnit 5, Gradle, Lombok, Spotless)
  modelled on previous tool, for a simple project management REST API (projects, tasks): project layout,
  ApiClient, Endpoints, tag-based suites, failure-only response logging, branded HTML report,
  testRunSummary.json, stability checks, and GitHub Actions CI with parallel suites and reporting.
  Use when setting up a personal API testing repo, adding API tests, suites, CI, or test reporting to it,
  or when the user mentions RestAssured, a project management / task tracker API test project, or
  "previous tool style" tests.
disable-model-invocation: true
---

# Scaffolding RestAssured API Tests (previous tool lite)

The system under test is a simple project management API
(projects containing tasks) reachable at `BASE_URL`.

## Stack

Java 17 toolchain, Gradle 9 wrapper, JUnit 5 (+ JUnit Pioneer for retries), RestAssured, Hamcrest,
Jackson, Lombok, Logback (SLF4J), Spotless (google-java-format).

## Target layout

```
project-tracker-api-tests/
├── build.gradle                     # suites, tag check, report branding, summary JSON
├── settings.gradle
├── scripts/
│   ├── run-suite.sh                 # suite ID -> Gradle task, non-blocking by default
│   └── run-stability-check.sh       # run a class/method N times before merging
├── .github/workflows/api-tests.yml  # PR + push + cron, matrix of suites, reports
├── docs/                            # README, guide, suites-and-ci, suite-mapping, triage-runbook
└── src/test/
    ├── java/
    │   ├── config/      Endpoints.java, TestConfig.java
    │   ├── utils/       ApiClient.java, ResponseLoggingExtension.java, TestTimeouts.java, JsonUtils.java
    │   ├── builders/    Lombok request POJOs (+ unit tests tagged "unit")
    │   └── apiTests/    projects/, tasks/, HealthTests.java
    └── resources/
        ├── fixtures/    JSON request bodies with @placeholder@ tokens
        └── logback.xml
```

Use the standard `src/test/java` layout (previous tool's `api-tests/` source-set override isn't worth it here).

## Workflow

Copy this checklist and track progress:

```
- [ ] 1. Scaffold Gradle project + wrapper
- [ ] 2. Add framework classes (config, utils)
- [ ] 3. Write first tests (health smoke + one resource)
- [ ] 4. Define suites (tags -> Gradle tasks -> suite IDs)
- [ ] 5. Reporting (branded HTML, summary JSON)
- [ ] 6. Scripts (run-suite, stability check)
- [ ] 7. CI (GitHub Actions)
- [ ] 8. Docs
```

**1. Scaffold.** `gradle init --type basic` (or copy an existing wrapper), then
`./gradlew wrapper`. Use the `build.gradle` in [templates.md](templates.md).

**2. Framework classes.** Copy `TestConfig`, `Endpoints`, `ApiClient`, `ResponseLoggingExtension`,
`TestTimeouts`, `JsonUtils` from [templates.md](templates.md). Rules:
- Tests never call RestAssured directly; every request goes through `ApiClient`.
- Every `ApiClient` method calls `ResponseLoggingExtension.setResponse(response, body)` (use `null` when there is no body).
- All paths live in `Endpoints` as `UPPER_SNAKE_CASE` constants; never inline a path in a test.
- Base URL comes from `-DbaseUrl` / `BASE_URL`, defaulting to `http://localhost:8080`.

**3. Tests.** Follow the conventions below and the example test class in [templates.md](templates.md).
Start with a `@Tag("smoke")` health check so CI can prove the app is up.

**4. Suites.** One JUnit tag per functional area, one Gradle task per tag, one kebab-case suite ID per task.
Keep the mapping in `docs/suite-mapping.md` and `scripts/run-suite.sh` in sync:

| Suite ID | Gradle task | JUnit tag |
|---|---|---|
| `smoke` | `testSmoke` | `smoke` |
| `projects` | `testProjects` | `projects` |
| `tasks` | `testTasks` | `tasks` |
| `unit` | `testUnit` | `unit` |

`verifyTestTags` (wired into `check`) fails the build if a test class has no `@Tag`.

**5. Reporting.** Every `Test` task is finalized by `testReportUI` (injects a banner + runbook link into
`build/reports/tests/<task>/index.html`) and `generateTestRunSummary` (parses JUnit XML into
`build/artifacts/testRunSummary.json` with totals, failed tests, and a re-run command per failure).

**6–7. Scripts and CI.** See [ci-and-reporting.md](ci-and-reporting.md).

**8. Docs.** `README.md` (install, run, lint, report, stability check),
`docs/guide.md` (how to write tests), `docs/suites-and-ci.md`, `docs/suite-mapping.md`, `docs/triage-runbook.md`.
A short ADR (why RestAssured over Postman/Pact) is a good portfolio touch.

## Test conventions

- **Arrange / Act / Assert**, one behaviour per test. No comments in tests; method name + `@DisplayName` explain intent.
- Class annotations: `@Tag("<suite>")` and `@ExtendWith(ResponseLoggingExtension.class)`.
- Every method gets a `@DisplayName` like `"GET /api/tasks/{id} returns 404 for unknown id"`.
- Assert `statusCode()` first, then key fields via `response.path(...)` with Hamcrest matchers.
  Assert exact status codes; body assertions can be more generic (type, presence, format).
- Per endpoint, cover: happy path → negative cases (400 validation, 404 not found) → for mutating endpoints, a modify/verify case.
- `@Timeout(value = TestTimeouts.S|M|L, unit = TimeUnit.SECONDS)`: S (5s) simple GET, M (15s) POST/PUT/PATCH/DELETE, L (30s) multi-step.
- `@RetryingTest(maxAttempts = 2)` instead of `@Test` only for genuinely transient-prone tests.
- Request bodies: Lombok `@Builder(toBuilder = true)` POJOs in `builders/` for structured bodies,
  or JSON fixtures in `resources/fixtures/` loaded with `JsonUtils.loadSubstituteJson(name, Map.of("key", "value"))`.
- Tests must be independent: each creates the project/tasks it needs (with a unique name) rather than relying on seed data or order.
- Quarantine a single test with `@Disabled("reason + ticket/issue link")`; quarantine a whole class by adding its
  FQCN pattern to `quarantined-tests.json`.

### Project management specifics

- **Lifecycle (CRUD) per resource:** create → read back → update → read back → delete → read returns 404.
- **Parent/child integrity:** a task created under a project appears in `GET /api/projects/{id}/tasks`;
  creating a task under an unknown project returns 404; deleting a project removes (or orphan-protects) its tasks —
  assert whichever behaviour the API defines.
- **Status workflow:** new tasks default to `TODO`; valid transitions (`TODO → IN_PROGRESS → DONE`) succeed;
  unknown statuses return 400. If the API forbids some transitions (e.g. `DONE → TODO`), test that explicitly.
- **Enums:** `status` and `priority` (`LOW | MEDIUM | HIGH`) only accept known values; assert with `oneOf(...)`.
- **Dates:** `dueDate` as ISO `yyyy-MM-dd`, `createdAt`/`updatedAt` as ISO 8601 instants; `updatedAt` changes after a PATCH,
  `createdAt` doesn't. Send dates as strings, not `LocalDate`, so Jackson needs no extra module.
- **Filtering and sorting:** `?status=DONE` returns only done tasks; `?priority=HIGH`, `?sort=dueDate` if supported.
- **Good negative cases:** blank/missing title, over-long title, invalid enum, malformed date, malformed JSON body,
  unknown project/task id, duplicate project name (if names must be unique).

## Before merging a new test

```bash
./gradlew spotlessApply
./gradlew test --tests "apiTests.tasks.TasksTests"
./scripts/run-stability-check.sh apiTests.tasks.TasksTests 5
./gradlew test --tests "apiTests.tasks.*"
open build/reports/tests/test/index.html
```

Finally, ask whether each new test adds real signal or just noise; drop the noise.

## Additional resources

- Gradle build file and all Java framework code: [templates.md](templates.md)
- Scripts, GitHub Actions workflow, summary JSON format, triage runbook outline: [ci-and-reporting.md](ci-and-reporting.md)
