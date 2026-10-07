# Benchmark

Feature tasks on [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template), pinned in `template.json`, scored by script with no LLM (ADR 0002).

Each task in `tasks/<task>/` has:

- `prompt.md`: what the agent sees
- `hidden/`: pytest files the agent never sees
- `task.json`: its Traps, each checked by hidden or template tests failing (`tests`), by changed files matching a glob (`changed`), or both
- `fixtures/`: patches against the pinned template, `good.patch` plus one `trap-<id>.patch` per Trap

`04-item-duplicate` is deliberately small, one endpoint a single session should handle well, so the results also show where the team is overkill.

`scorer/score.mjs` takes a finished working tree and a task and returns pass or fail per hidden test and per Trap. It runs the tests in Docker against a throwaway Postgres (`scorer/compose.yml`), using the template's own tests as pinned rather than any edits the agent made to them.

`node --test` checks every task's fixtures: the good one passes every hidden test and trips no Trap, and each trap fixture trips only its own Trap. It also checks that the tasks together cover every Trap kind and that at least one needs UI work. Those checks need Docker running (Docker Desktop, OrbStack or Colima) and are skipped without it. Work copies go in `~/.cache/rolecall/`, because Colima shares only your home directory with its VM.
