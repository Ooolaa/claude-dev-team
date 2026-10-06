#!/usr/bin/env bash
# Installs the five-agent dev team for Claude Code (user scope).
set -euo pipefail
cd "$(dirname "$0")"

command -v claude >/dev/null || { echo "claude CLI not found"; exit 1; }
command -v jq >/dev/null || { echo "jq not found (brew install jq)"; exit 1; }

echo "Adding plugin marketplaces..."
claude plugin marketplace add DietrichGebert/ponytail
claude plugin marketplace add JuliusBrussee/caveman
claude plugin marketplace add obra/superpowers
claude plugin marketplace add multica-ai/andrej-karpathy-skills
claude plugin marketplace add mattpocock/skills
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin marketplace add Leonxlnx/taste-skill
claude plugin marketplace add pbakaus/impeccable

echo "Installing plugins..."
claude plugin install ponytail@ponytail -y
claude plugin install caveman@caveman -y
claude plugin install superpowers@superpowers-dev -y
claude plugin install andrej-karpathy-skills@karpathy-skills -y
claude plugin install mattpocock-skills@mattpocock -y
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill -y
claude plugin install taste-skill@taste-skill -y
claude plugin install impeccable@impeccable -y

echo "Fetching steipete/agent-rules..."
tmp=$(mktemp -d)
git clone --depth 1 -q https://github.com/steipete/agent-rules.git "$tmp/agent-rules"
mkdir -p ~/.claude/agent-rules/steipete
cp -R "$tmp/agent-rules/project-rules" "$tmp/agent-rules/global-rules" ~/.claude/agent-rules/steipete/
rm -rf "$tmp"

echo "Installing agents and the /dev-team skill..."
mkdir -p ~/.claude/agents ~/.claude/skills
cp agents/team-*.md ~/.claude/agents/
cp -R skills/dev-team ~/.claude/skills/

echo "Enabling agent teams..."
settings=~/.claude/settings.json
[ -f "$settings" ] || echo '{}' > "$settings"
cp "$settings" "$settings.bak-$(date +%Y%m%d%H%M%S)"
jq '.env = ((.env // {}) + {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"})' "$settings" > "$settings.tmp"
mv "$settings.tmp" "$settings"

# Keep caveman's voice inside the Caveman agent instead of every session.
cfg="${XDG_CONFIG_HOME:-$HOME/.config}/caveman/config.json"
mkdir -p "$(dirname "$cfg")"
[ -f "$cfg" ] || echo '{ "defaultMode": "off" }' > "$cfg"

echo "Done. Restart Claude Code, then run: /dev-team <your task>"
