# Regression analysis (Draft)

- **Range:** `a6da44d..0c19c1d` (0c19c1d^1 to 0c19c1d, PR #2)
- **Files:** 2 changed: 1 analysed, 1 ignored
- **Areas:** Web UI (Medium)
- **Highest risk:** Medium
- **Suite source:** api-tests/scripts/run-suite.sh (no mapping file)

## 1. Manual test cases

| # | Test case | Expected behaviour | Risk | Source | Status |
|---|---|---|---|---|---|
| 1 | With the app running and no projects stored, open http://localhost:8080 | Page loads with the Projects section; "No projects yet." is shown and the tasks section is hidden | Medium: the page renders its list from the `GET /api/projects` response on load | `src/main/resources/static/index.html:124` | Draft |
| 2 | Create a project with a name and an empty description | Project appears in the list with an empty description cell; the form clears | Medium: an empty description is sent as `null` rather than an empty string | `src/main/resources/static/index.html:148` | Draft |
| 3 | Submit the create-project form with a blank name | The server's reason appears at the top of the page; no row is added | Medium: errors only surface if the API returns an `error` field the page can read | `src/main/resources/static/index.html:98` | Draft |
| 4 | Open a project, then rename it; separately, start a rename and cancel the prompt | After rename, both the list row and the "Tasks for" heading show the new name; after cancel, nothing changes | Medium: the heading only refreshes when the renamed project is the open one | `src/main/resources/static/index.html:160` | Draft |
| 5 | Open a project, delete it and confirm; on another project, cancel the confirm dialog | Confirmed: row removed and tasks section hidden. Cancelled: project remains | Medium: a confirmed delete removes the project and all its tasks; the open-project state must be cleared | `src/main/resources/static/index.html:166` | Draft |
| 6 | In an open project, add a task with a title only (priority left at default, no due date) | Row shows priority MEDIUM and due "—"; after submit the priority selector resets to MEDIUM | Medium: due date is omitted from the request when empty and the default priority is re-applied after reset | `src/main/resources/static/index.html:219` | Draft |
| 7 | Change a task's status via its dropdown, including a change the API rejects | Accepted: dropdown shows the new status after the list reloads. Rejected: the server's reason is shown and the dropdown returns to the saved status | Medium: the list reloads after every status change, whether or not the update succeeded | `src/main/resources/static/index.html:229` | Draft |
| 8 | Combine the status and priority filters, including a combination with no matches | Only matching tasks are listed; with no matches, "No tasks to show." appears | Medium: filters are sent as query parameters and only when a value is selected | `src/main/resources/static/index.html:189` | Draft |
| 9 | Create a project and a task whose names contain `<b>x</b>` | The text is displayed literally, not rendered as bold | Medium: all row content is built client-side from API data | `src/main/resources/static/index.html:79` | Draft |
| 10 | After the UI is added, call `GET /health` and an unknown `/api/projects/{id}` | `/health` still replies `{"status":"ok"}`; API errors still come back as JSON | Medium: a page is now served from the root path alongside the API | `src/main/resources/static/index.html:1`, `README.md:36` | Draft |

## 2. Suite recommendations

| Suite | Why (tied to the diff) | Narrow to | Runs in PR CI | Run command |
|---|---|---|---|---|
| None | The only analysed change is the browser UI; `smoke` and `projects` exercise the HTTP API, and no API code changed in this range | n/a | n/a | n/a |

## Flags

- Area judged, not mapped: `src/main/resources/static/index.html` assigned to Web UI
- Ambiguity: `src/main/resources/static/index.html:7`: the stylesheet loads from an external CDN; the diff doesn't say how the page should behave when it can't be reached (needs: whether offline/unstyled use is supported)
