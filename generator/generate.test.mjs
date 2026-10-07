import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { generate } from './generate.mjs';

const rolesDir = fileURLToPath(new URL('../roles/', import.meta.url));
const agentsDir = fileURLToPath(new URL('../agents/', import.meta.url));
const freshDir = () => mkdtemp(join(tmpdir(), 'rolecall-'));

async function skeptic() {
  const dir = await freshDir();
  await generate({ rolesDir, outDir: dir });
  return readFile(join(dir, 'team-skeptic.md'), 'utf8');
}

test('Skeptic Role file has name, description, model and instructions', async () => {
  const file = await skeptic();
  const [, frontmatter, body] = file.split(/^---$/m);
  assert.match(frontmatter, /^name: team-skeptic$/m);
  assert.match(frontmatter, /^description: ".+"$/m);
  assert.match(frontmatter, /^model: \S+$/m);
  assert.match(body, /You are the \*\*Skeptic\*\*/);
});

test('Skeptic Role file credits its Upstream', async () => {
  const file = await skeptic();
  assert.match(file, /andrej-karpathy-skills/);
  assert.match(file, /https:\/\/github\.com\/multica-ai\/andrej-karpathy-skills/);
  assert.match(file, /MIT/);
});

test('Skeptic Role file scopes the Teammate to its own skill plus the Base rule', async () => {
  const file = await skeptic();
  assert.match(file, /`andrej-karpathy-skills:karpathy-guidelines`/);
  assert.match(file, /`ponytail:ponytail`/);
  assert.match(file, /Ignore every other skill/);
});

test('stale check passes when files match fresh output', async () => {
  const dir = await freshDir();
  await generate({ rolesDir, outDir: dir });
  assert.deepEqual(await generate({ rolesDir, outDir: dir, check: true }), []);
});

test('stale check reports drifted and missing files without writing', async () => {
  const dir = await freshDir();
  await generate({ rolesDir, outDir: dir });
  await writeFile(join(dir, 'team-skeptic.md'), 'hand edit');
  assert.deepEqual(await generate({ rolesDir, outDir: dir, check: true }), ['team-skeptic.md']);
  assert.equal(await readFile(join(dir, 'team-skeptic.md'), 'utf8'), 'hand edit');

  const empty = await freshDir();
  assert.deepEqual(await generate({ rolesDir, outDir: empty, check: true }), ['team-skeptic.md']);
  assert.deepEqual(await readdir(empty), []);
});

test('committed Role files are up to date', async () => {
  assert.deepEqual(await generate({ rolesDir, outDir: agentsDir, check: true }), []);
});
