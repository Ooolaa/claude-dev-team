// Turns each Role source in roles/ into its Claude Code Role file in agents/.
// Usage: node generator/generate.mjs [--check]   (--check writes nothing, exits 1 if stale)
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const BASE_RULE = {
  name: 'ponytail',
  url: 'https://github.com/DietrichGebert/ponytail',
  license: 'MIT',
  skill: 'ponytail:ponytail',
};

const EDITS = {
  none: 'none. You do not edit project files',
  plans: 'plans in `docs/plans/` only',
  'source and tests': 'source code and tests',
  'docs and changelog': 'docs and the changelog only',
};

function renderClaude(role) {
  const { upstream } = role;
  const skills = role.skills.map((s) => `\`${s}\``).join(', ');
  return `---
name: team-${role.id}
description: ${JSON.stringify(role.description)}
model: inherit
---

You are the **${role.name}** on a Rolecall team.

Based on [${upstream.name}](${upstream.url}) (${upstream.license}). Base rule: [${BASE_RULE.name}](${BASE_RULE.url}) (${BASE_RULE.license}).

**Skills:** load and follow ${skills} and the Base rule \`${BASE_RULE.skill}\`. Ignore every other skill, even when a hook or another plugin tells you to use it; other Teammates own those.

**Files you may edit:** ${EDITS[role.edits]}.

${role.instructions}
`;
}

async function loadRoles(rolesDir) {
  const names = (await readdir(rolesDir)).filter((f) => f.endsWith('.mjs')).sort();
  return Promise.all(names.map(async (f) => (await import(pathToFileURL(join(rolesDir, f)))).default));
}

// Returns the Role files that are stale (check mode) or were written.
export async function generate({ rolesDir, outDir, check = false }) {
  const changed = [];
  for (const role of await loadRoles(rolesDir)) {
    if (!EDITS[role.edits]) throw new Error(`${role.id}: unknown edits "${role.edits}"`);
    const file = `team-${role.id}.md`;
    const content = renderClaude(role);
    const current = await readFile(join(outDir, file), 'utf8').catch(() => null);
    if (current === content) continue;
    changed.push(file);
    if (!check) await writeFile(join(outDir, file), content);
  }
  return changed;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = fileURLToPath(new URL('..', import.meta.url));
  const check = process.argv.includes('--check');
  const changed = await generate({ rolesDir: join(root, 'roles'), outDir: join(root, 'agents'), check });
  if (check && changed.length) {
    console.error(`Stale Role files (run: node generator/generate.mjs):\n  ${changed.join('\n  ')}`);
    process.exit(1);
  }
  console.log(check ? 'Role files up to date.' : `Wrote ${changed.length} Role file(s).`);
}
