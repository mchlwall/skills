# test-plan-generator example

## Input

[project-manager `README.md`](https://github.com/mchlwall/project-manager/blob/e738e6f/README.md) at `e738e6f`, regression mode, feature "Tasks". The plan draws mainly on these lines:

```
| `POST /api/projects/{id}/tasks` | Adds a task to a project (title required) |
| `GET /api/projects/{id}/tasks` | Lists a project's tasks, optionally `?status=` and/or `?priority=` |
| `GET /api/tasks/{id}` | Gets one task |
| `PATCH /api/tasks/{id}` | Changes a task's details |
| `DELETE /api/tasks/{id}` | Deletes a task |
**Task fields:** `id`, `projectId`, `title`, `description`,
`status` (`TODO`, `IN_PROGRESS`, `DONE`; starts as `TODO`),
`priority` (`LOW`, `MEDIUM`, `HIGH`; starts as `MEDIUM`),
`dueDate` (for example `2026-12-01`), `createdAt`, `updatedAt`
You can create, rename and delete projects, then open a project to add tasks, change their status, filter them and delete them.
```

## What I changed

- [test-report.md](test-report.md) is the skill's output exactly as generated, before review.

## How to reproduce

With the skill installed and the project-manager repo checked out at `e738e6f`, prompt:

```
Use the test-plan-generator skill in regression mode for the "Tasks" feature, using project-manager/README.md as the source.
```

Environments, reason for change and known risks were left unset, so the environments defaulted to the two surfaces the README describes: API and Browser.
