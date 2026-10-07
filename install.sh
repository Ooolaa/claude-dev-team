#!/usr/bin/env bash
# Installs Rolecall for Claude Code (user scope).
# Usage: ./install.sh              install
#        ./install.sh --uninstall  remove everything install added
set -euo pipefail
cd "$(dirname "$0")"

command -v claude >/dev/null || { echo "claude CLI not found"; exit 1; }
command -v jq >/dev/null || { echo "jq not found (brew install jq)"; exit 1; }

# GitHub repo, marketplace name, plugin name — one line per Upstream installed as a plugin.
UPSTREAMS="
DietrichGebert/ponytail ponytail ponytail
JuliusBrussee/caveman caveman caveman
obra/superpowers superpowers-dev superpowers
multica-ai/andrej-karpathy-skills karpathy-skills andrej-karpathy-skills
mattpocock/skills mattpocock mattpocock-skills
nextlevelbuilder/ui-ux-pro-max-skill ui-ux-pro-max-skill ui-ux-pro-max
Leonxlnx/taste-skill taste-skill taste-skill
pbakaus/impeccable impeccable impeccable
"
# Person-named agent files from before the Roles were named by job.
OLD_AGENTS="karpathy superpowers mattpocock steipete caveman promax taste impeccable"
CAVEMAN_OFF='{ "defaultMode": "off" }'

settings=~/.claude/settings.json
cfg="${XDG_CONFIG_HOME:-$HOME/.config}/caveman/config.json"

remove_old_agents() {
  for a in $OLD_AGENTS; do rm -f ~/.claude/agents/team-$a.md; done
}

backup_settings() {
  [ -f "$settings" ] || echo '{}' > "$settings"
  cp "$settings" "$settings.bak-$(date +%Y%m%d%H%M%S)"
}

if [ "${1:-}" = "--uninstall" ]; then
  echo "Removing Role files and the /dev-team skill..."
  for f in agents/team-*.md; do rm -f ~/.claude/agents/"$(basename "$f")"; done
  remove_old_agents
  rm -rf ~/.claude/skills/dev-team ~/.claude/agent-rules/steipete

  echo "Uninstalling plugins and marketplaces..."
  while read -r repo market plugin <&3; do
    [ -n "$repo" ] || continue
    claude plugin uninstall "$plugin@$market" || true
    claude plugin marketplace remove "$market" || true
  done 3<<< "$UPSTREAMS"

  echo "Disabling agent teams..."
  backup_settings
  jq 'del(.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS)' "$settings" > "$settings.tmp"
  mv "$settings.tmp" "$settings"

  # Only remove the caveman config if it is still the one install wrote.
  [ "$(cat "$cfg" 2>/dev/null)" = "$CAVEMAN_OFF" ] && rm "$cfg"

  echo "Rolecall uninstalled. Restart Claude Code."
  exit 0
fi

echo "Adding plugin marketplaces and installing plugins..."
while read -r repo market plugin <&3; do
  [ -n "$repo" ] || continue
  claude plugin marketplace add "$repo"
  claude plugin install "$plugin@$market" -y
done 3<<< "$UPSTREAMS"

echo "Fetching steipete/agent-rules..."
tmp=$(mktemp -d)
git clone --depth 1 -q https://github.com/steipete/agent-rules.git "$tmp/agent-rules"
mkdir -p ~/.claude/agent-rules/steipete
cp -R "$tmp/agent-rules/project-rules" "$tmp/agent-rules/global-rules" ~/.claude/agent-rules/steipete/
rm -rf "$tmp"

echo "Installing Role files and the /dev-team skill..."
mkdir -p ~/.claude/agents ~/.claude/skills
remove_old_agents
cp agents/team-*.md ~/.claude/agents/
cp -R skills/dev-team ~/.claude/skills/

echo "Enabling agent teams..."
backup_settings
jq '.env = ((.env // {}) + {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"})' "$settings" > "$settings.tmp"
mv "$settings.tmp" "$settings"

# Keep caveman's voice inside the Reviewer instead of every session.
mkdir -p "$(dirname "$cfg")"
[ -f "$cfg" ] || echo "$CAVEMAN_OFF" > "$cfg"

echo "Rolecall installed. Restart Claude Code, then run: /dev-team <your task>"
