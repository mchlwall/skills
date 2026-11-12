# skills

## What is a skill?

A skill is a packaged set of instructions Claude Code can invoke to perform specialized tasks like scaffolding projects, running reviews, or following repo-specific workflows. Skills are loaded via the `Skill` tool and give Claude detailed guidance for particular kinds of work.

## What this builds

This repository contains reusable scaffolding skills for Claude Code. Currently it includes `scaffolding-restassured-api-tests`, which scaffolds a complete Java API test framework using RestAssured, JUnit 5, Gradle, and Lombok for testing project management/task tracker APIs.

**Generated repository:** [project-tracker-api-tests](https://github.com/mwall/project-tracker-api-tests)

## Installing in Claude

1. Clone this repository to your local machine
2. Add it to your Claude Code project settings in `.claude/settings.json`:

```json
{
  "skills": [
    "/Users/mwall/Github/skills/skills"
  ]
}
```

3. The skills will be available in any Claude Code conversation in that project
4. For global availability across all projects, add the path to `~/.claude/settings.json` instead

Once installed, invoke with: `/scaffolding-restassured-api-tests` or by mentioning "RestAssured API tests" or "project management API tests" in your prompt.
