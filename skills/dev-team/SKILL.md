---
name: dev-team
description: Launch the eight-agent dev team (Skeptic, Superpowers, Mattpocock, Steipete, Caveman, plus designers ProMax, Taste, Impeccable) as an agent team that discusses and builds a task together. Use when the user says "/dev-team", "start the dev team", "run the team on this", or asks the team agents to work on a project.
---

# Dev team

You are the team lead. The user's task is in the arguments; if none, ask for it in one line.

## Spawn

Spawn eight **teammates** (agent team, not plain subagents), using these names and agent types:

| Name | Agent type | Role |
|---|---|---|
| Skeptic | team-skeptic | skeptic: assumptions, success criteria, scope guard |
| Superpowers | team-superpowers | planner: design + task plan in docs/plans/ |
| Mattpocock | team-mattpocock | builder: test-first implementation, only one who edits code |
| Steipete | team-steipete | quality gate: build/lint/test, docs, changelog |
| Caveman | team-caveman | reviewer: terse diff review + final summary |
| ProMax | team-promax | design-system lead: palette, type, spacing, UX rules (advises only) |
| Taste | team-taste | art director: visual direction, anti-generic (advises only) |
| Impeccable | team-impeccable | design critic: audits screenshots, sends polish fixes (advises only) |

For work with no UI at all, skip the three designers.

Spawn every teammate while the session's working directory is the project root. Give each the user's task, the project path, the starting commit (`git rev-parse HEAD`, if it's a git repo), and the table above so they know who plays which role.

## Flow

Put these on the shared task list with dependencies:

1. **Discuss** (in parallel): Skeptic sends the brief; Steipete finds the build/test commands; Superpowers reads the code; Taste and ProMax agree a visual direction and design spec and send it to Superpowers. Have them message each other to challenge the brief.
2. **Ask:** bring any open questions from Skeptic to the user. Wait for answers.
3. **Plan:** Superpowers writes the plan; Skeptic challenges it once. Show the user the plan summary and get a go-ahead.
4. **Build:** Mattpocock implements task by task. Steipete checks each task; Impeccable audits screenshots of each visual task; Skeptic guards scope.
5. **Review:** Caveman reviews the diff; Mattpocock fixes; Steipete runs the final checks and updates docs/changelog.
6. **Wrap up:** relay Caveman's summary and Steipete's draft commit message. Commit or push only if the user says so. Then shut the team down.

## Rules

- Wait for teammates; don't do their work yourself.
- Only Mattpocock edits source and tests, only Superpowers writes plans, and only Steipete edits docs and the changelog. The designers advise only. This prevents overwrites.
- For a tiny task (one-line fix, a question), tell the user a team is overkill and do it directly unless they insist.
