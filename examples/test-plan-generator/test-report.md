# Test plan (Draft): Tasks (regression)

- **Source:** `project-manager/README.md` at `e738e6f` (Running it, Using it in a browser, What the API does)
- **Reason for change:** not given
- **Environments:** API, Browser

## Smoke checks

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 1 | User calls `GET /health` | Replies `{"status":"ok"}` | | N/A | | `README.md:21` |
| 2 | User opens http://localhost:8080 | The page loads with the projects list | N/A | | | `README.md:40` |
| 3 | User opens a project in the browser | The project's tasks are shown with controls to add tasks | N/A | | | `README.md:41` |

## Core behaviour

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 4 | User adds a task to a project with only a title | Task is created with status `TODO` and priority `MEDIUM` | | | | `README.md:76`, `README.md:85-86` |
| 5 | User adds a task with title, description, priority `HIGH` and due date `2026-12-01` | Task is created with exactly those values | | N/A | UI fields for description, priority and due date not described in source | `README.md:76`, `README.md:84-87` |
| 6 | User lists a project's tasks | Every task belonging to that project is returned, and no others | | | | `README.md:77` |
| 7 | User gets one task by id | The task is returned with `id`, `projectId`, `title`, `description`, `status`, `priority`, `dueDate`, `createdAt`, `updatedAt` | | N/A | | `README.md:78`, `README.md:84-87` |
| 8 | User changes a task's status from `TODO` to `IN_PROGRESS` | Task shows status `IN_PROGRESS` | | | | `README.md:79`, `README.md:41` |
| 9 | User changes a task's title | Task shows the new title | | N/A | Source only describes status changes in the browser | `README.md:79` |
| 10 | User deletes a task | Task no longer appears in the project's task list | | | | `README.md:80`, `README.md:41` |

## Options and settings

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 11 | User filters a project's tasks by status `DONE` | Only `DONE` tasks are listed | | | | `README.md:77`, `README.md:41` |
| 12 | User filters a project's tasks by priority `HIGH` | Only `HIGH` tasks are listed | | | | `README.md:77`, `README.md:41` |
| 13 | User filters by status `TODO` and priority `LOW` together | Only tasks matching both are listed | | | | `README.md:77` |
| 14 | User removes all filters | All of the project's tasks are listed again | | | | `README.md:77` |
| 15 | User changes a task's priority from `MEDIUM` to `LOW` | Task shows priority `LOW` | | N/A | Source doesn't describe changing priority in the browser | `README.md:79`, `README.md:86` |
| 16 | User changes a task's status from `DONE` back to `TODO` | Not stated: confirm with owner | | | Assumption: allowed transitions not documented | `README.md:79`, `README.md:85` |

## Regression risk areas

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 17 | User deletes a project that has tasks | The project and all of its tasks are deleted | | | Guards against orphaned tasks surviving a project delete | `README.md:75` |
| 18 | User changes a task's details and reads it back | Not stated: confirm with owner | | N/A | Assumption: guards `updatedAt` changing and `createdAt` staying fixed; behaviour not documented | `README.md:79`, `README.md:87` |
| 19 | User adds a task with a blank title | Rejected; API body is `{"error": "..."}` and the browser shows the reason at the top of the page | | | Guards the shared error format the page relies on to display messages | `README.md:65-66`, `README.md:76`, `README.md:41` |
| 20 | User restarts the app after adding tasks | Previously added tasks are still listed | | | Guards persistence to the database file across restarts | `README.md:7`, `README.md:22-25` |

## Edge cases and resilience

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 21 | User adds a task with status `BLOCKED` | Not stated: confirm with owner | | N/A | Assumption: only `TODO`, `IN_PROGRESS`, `DONE` are documented | `README.md:85` |
| 22 | User adds a task with priority `URGENT` | Not stated: confirm with owner | | N/A | Assumption: only `LOW`, `MEDIUM`, `HIGH` are documented | `README.md:86` |
| 23 | User adds a task with due date `01/12/2026` | Not stated: confirm with owner | | N/A | Assumption: only the `2026-12-01` format is shown | `README.md:87` |
| 24 | User adds a task to a project id that doesn't exist | Not stated: confirm with owner | | N/A | Assumption: any error should follow the `{"error"}` format | `README.md:76`, `README.md:65-66` |
| 25 | User gets a task id that doesn't exist | Not stated: confirm with owner | | N/A | Assumption | `README.md:78` |
| 26 | User adds a task with a 1,000-character title | Not stated: confirm with owner | | | Assumption: no length limit documented | `README.md:76` |
| 27 | User submits the add-task form twice in quick succession | Not stated: confirm with owner | N/A | | Assumption | `README.md:41` |
| 28 | User reloads the page after changing a task's status | The changed status is still shown | N/A | | | `README.md:41`, `README.md:7` |

## Contexts

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 29 | HTTP client against the JSON API | | | N/A | | `README.md:63-80` |
| 30 | Browser UI at http://localhost:8080 | | N/A | | | `README.md:38-41` |
| 31 | App run with Docker (data in `data/`) | | | | | `README.md:15-25` |
| 32 | App run with local Java (data in `project-manager.db`) | | | | | `README.md:27-36` |

## Accessibility and quality

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 33 | User adds, filters and deletes a task using only the keyboard | Not stated: confirm with owner | N/A | | Assumption | `README.md:41` |
| 34 | User moves through task controls with a screen reader | Not stated: confirm with owner | N/A | | Assumption | `README.md:41` |
| 35 | User opens a project with the browser console open | Not stated: confirm with owner | N/A | | Assumption: no console errors expected | `README.md:40-41` |

## Closure

| # | Test case | Expected | API | Browser | Notes | Source |
|---|---|---|---|---|---|---|
| 36 | Time-boxed exploratory session | | | | | |
| 37 | Element and layout check | | | | | |
| 38 | Accessibility check | | | | | |
| 39 | Localisation check | | | | | |

## Regression surface

| Contexts counted | Grade | Action |
|---|---|---|
| 4: API, Browser UI, Docker run, local Java run | Elevated | Every context has its own row (#29 to #32, confirmed) |

## Exploratory testing
- **Status transitions:** try every move between `TODO`, `IN_PROGRESS` and `DONE`, in both directions. The source lists the values and the default but not which moves are allowed.
- **Editing in the browser:** check which task fields can be changed from the page. The source only mentions changing status.
- **Validation responses:** probe invalid enums, bad dates and unknown ids for status codes and messages. The source documents only the error body shape.
- **Data location:** switch between the Docker and local Java runs and compare what is listed. The source says they store data in different places but not whether that's expected to be visible to users.
- **Due dates:** try past dates, leap days and clearing a due date. The source gives one example format and nothing else.
