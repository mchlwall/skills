# Test Engineering Skills

- Reusable instruction sets for Claude that encode how I build and run test tooling
- A skill is a folder of instructions and templates that Claude loads when a task matches its description

## Skills

| Skill | What it does | Produced |
|---|---|---|
| [scaffolding-restassured-api-tests](skills/scaffolding-restassured-api-tests) | Scaffolds and grows a Java API test suite (RestAssured, JUnit 5, Maven): tag-based suites, failure-only response logging, machine-readable run summaries, stability checks, and a parallel GitHub Actions matrix with aggregated reports | [`api-tests/` in project-tracker](https://github.com/<you>/project-tracker/tree/main/api-tests) |

## Installing a skill

Copy the skill folder into your Claude skills directory (for example `~/.claude/skills/`), or add this repository as a skills source in your Claude configuration. Claude picks the skill up automatically when a request matches its `description` in `SKILL.md`.

## How these are built

Each skill starts from conventions proven in real test frameworks, written up as instructions with templates, then used to generate a working repository. The generated repository is linked above so the skill can be judged by its output. See [docs/how-skills-are-built.md](docs/how-skills-are-built.md).

## Contributing

Issues and pull requests are welcome, particularly reports of a skill producing something that didn't match its description.

## Licence

MIT