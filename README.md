# Test Engineering Skills

Reusable instruction sets for Claude that encode how I build and run test tooling. A skill is a folder of instructions, templates and (occasionally) a script that Claude loads when a request matches its `description` in `SKILL.md`.

## Skills

| Skill | What it does | Example |
|---|---|---|
| [scaffolding-restassured-api-tests](skills/scaffolding-restassured-api-tests) | Scaffolds and grows a Java API test suite: tag-based suites, failure-only logging, run summaries, CI | [`api-tests/` in project-manager](https://github.com/mchlwall/project-manager/tree/main/api-tests) |
| [regression-analyzer](skills/regression-analyzer) | Turns a branch diff into risk-weighted manual test cases and the smallest set of suites to run | [examples/regression-analyzer](examples/regression-analyzer) |
| [test-plan-generator](skills/test-plan-generator) | Writes a regression or new-feature test plan from docs, a brief or a spec | [examples/test-plan-generator](examples/test-plan-generator) |
| [test-report-generator](skills/test-report-generator) | Summarises an executed test plan into a verdict, pass rate and per-area counts (script-counted) | [examples/test-report-generator](examples/test-report-generator) |

## Installing

Copy a skill folder into your Claude skills directory (for example `~/.claude/skills/`), or clone this repository and add its `skills/` folder as a skills source in your Claude configuration. Invoke a skill by name (for example `/test-plan-generator`) or just describe the task; Claude picks the skill whose description matches.

## How these are built

Each skill starts from conventions proven in real test work, written up as instructions with templates, then run against a real repository. Every skill links to its output above so it can be judged by what it produces. Each example folder shows the input, any edits made to the raw output, and how to reproduce it.

## Contributing

Issues and pull requests are welcome, particularly reports of a skill producing something that didn't match its description.

## Licence

MIT
