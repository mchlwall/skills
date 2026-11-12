# regression-analyzer example

## Input

[project-manager PR #2](https://github.com/mchlwall/project-manager/pull/2) ("Basic UI"), analysed as the range `0c19c1d^1..0c19c1d`:

```
M  README.md                              (ignored: docs)
A  src/main/resources/static/index.html   (analysed: 259-line single-page UI for projects and tasks)
2 files changed, 267 insertions(+), 8 deletions(-)
```

## What happened

- [test-report.md](test-report.md) is the skill's output exactly as generated, before review.

## How to reproduce

With the skill installed and the project-manager repo checked out, prompt:

```
Run the regression-analyzer skill on the project-manager repo with base 0c19c1d^1 and head 0c19c1d.
```

To inspect the same input by hand:

```bash
git diff --name-status 0c19c1d^1 0c19c1d
git diff -U5 0c19c1d^1 0c19c1d -- src/main/resources/static/index.html
```
