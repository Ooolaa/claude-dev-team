# Claude Dev Team

Five well-known agent rule sets, turned into five Claude Code agents that discuss a task, challenge each other, and build it together.

```
/dev-team add offline caching to the article list
```

Each agent is based on one popular open-source project and keeps that project's way of thinking:

| Agent | Based on | Role | Edits |
|---|---|---|---|
| **Karpathy** | [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | Skeptic: reads the code, states assumptions, asks questions, sets success criteria, keeps changes small | Nothing |
| **Superpowers** | [obra/superpowers](https://github.com/obra/superpowers) | Planner: writes the design and a step-by-step plan | `docs/plans/` |
| **Mattpocock** | [mattpocock/skills](https://github.com/mattpocock/skills) | Builder: implements test-first and debugs methodically | Source and tests |
| **Steipete** | [steipete/agent-rules](https://github.com/steipete/agent-rules) | Quality gate: build, lint, tests, docs, changelog | Docs and changelog |
| **Caveman** | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Reviewer: terse diff review and final summary | Nothing |

[Ponytail](https://github.com/DietrichGebert/ponytail) runs underneath all of them as an always-on rule: write only the code the task needs.

## How it works

The `/dev-team` skill makes your Claude Code session the **team lead**. It spawns the five agents as an [agent team](https://code.claude.com/docs/en/agent-teams): separate Claude sessions with a shared task list that message each other directly.

```
1. Discuss   Karpathy writes the brief, Steipete finds the build/test commands,
             Superpowers reads the code. They challenge each other.
2. Ask       Open questions come to you. The team waits for answers.
3. Plan      Superpowers writes the plan, Karpathy pushes back once.
             You approve it before any code is written.
4. Build     Mattpocock builds task by task, test-first.
             Steipete checks every task, Karpathy guards scope.
5. Review    Caveman reviews the diff, Mattpocock fixes,
             Steipete runs final checks and updates docs.
6. Wrap up   You get a summary and a draft commit message.
             Nothing is committed or pushed unless you say so.
```

Every agent owns its own set of files, so they never overwrite each other's work.

## Install

Requires [Claude Code](https://code.claude.com), `git`, `jq` and `node`.

```bash
git clone https://github.com/Ooolaa/claude-dev-team.git
cd claude-dev-team
./install.sh
```

The script:

- installs the plugins for ponytail, caveman, superpowers, andrej-karpathy-skills and mattpocock/skills
- copies steipete/agent-rules to `~/.claude/agent-rules/steipete/`
- copies the five agents to `~/.claude/agents/` and the skill to `~/.claude/skills/dev-team/`
- enables agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) in `~/.claude/settings.json`, after backing it up
- turns caveman's always-on voice off, so only the Caveman agent talks that way

Restart Claude Code afterwards.

## Usage

Open a project, start `claude`, and type:

```
/dev-team <what you want built>
```

In the agent panel below the prompt, use ↑/↓ to select an agent and Enter to read its transcript or message it directly. For split panes (one per agent), run inside tmux or iTerm2 and set `"teammateMode": "auto"` in `~/.claude/settings.json`.

## Things to know

- **Cost:** five agents use roughly five times the tokens of one session. Use the team for real features, not one-line fixes. The lead will tell you when a task is too small.
- **Agent teams are experimental** in Claude Code. Sessions with in-process teammates can't be resumed, and task status sometimes lags.
- **Overlaps:** superpowers and mattpocock/skills both ship test-driven development, debugging and review skills. The agent files decide which one each agent uses. Superpowers also loads a short guide into every session; `claude plugin disable superpowers` turns that off.
- **Delegation changes:** with agent teams on, Claude may start teammates on its own when it delegates work. Set the variable to `0` to switch back.

## Uninstall

```bash
rm ~/.claude/agents/team-{karpathy,superpowers,mattpocock,steipete,caveman}.md
rm -r ~/.claude/skills/dev-team ~/.claude/agent-rules/steipete
for p in ponytail caveman superpowers andrej-karpathy-skills mattpocock-skills; do claude plugin uninstall $p; done
```

Then remove `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` from the `env` block of `~/.claude/settings.json`.

## Credits

This repo only contains the agent definitions, the `/dev-team` skill and an install script. All the rules come from these projects, installed from their own repositories:

- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert (MIT)
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee (Apache 2.0)
- [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent (MIT)
- [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock (MIT)
- [steipete/agent-rules](https://github.com/steipete/agent-rules) by Peter Steinberger (MIT)
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills), based on Andrej Karpathy's notes on LLM coding pitfalls

## License

[MIT](LICENSE)
