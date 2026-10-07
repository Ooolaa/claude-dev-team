import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { generate } from './generate.mjs';

const rolesDir = fileURLToPath(new URL('../roles/', import.meta.url));
const agentsDir = fileURLToPath(new URL('../agents/', import.meta.url));
const freshDir = () => mkdtemp(join(tmpdir(), 'rolecall-'));

const roles = await Promise.all(
  (await readdir(rolesDir)).map(async (f) => (await import(pathToFileURL(join(rolesDir, f)))).default),
);
const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const generated = await freshDir();
await generate({ rolesDir, outDir: generated });
const roleFile = (role) => readFile(join(generated, `team-${role.id}.md`), 'utf8');

test('there is one Role source per Role, named by job', () => {
  assert.deepEqual(roles.map((r) => r.name).sort(), [
    'Art Director', 'Builder', 'Design Critic', 'Design Lead',
    'Gatekeeper', 'Planner', 'Reviewer', 'Skeptic',
  ]);
});

test('generator writes exactly one Role file per Role and nothing else', async () => {
  assert.deepEqual((await readdir(generated)).sort(), roles.map((r) => `team-${r.id}.md`).sort());
});

for (const role of roles) {
  test(`${role.name}: Role file has name, description, model and instructions`, async () => {
    const [, frontmatter, body] = (await roleFile(role)).split(/^---$/m);
    assert.match(frontmatter, new RegExp(`^name: team-${role.id}$`, 'm'));
    assert.match(frontmatter, /^description: ".+"$/m);
    assert.match(frontmatter, /^model: \S+$/m);
    assert.match(body, new RegExp(`You are the \\*\\*${role.name}\\*\\*`));
    assert.ok(body.includes(role.instructions));
  });

  test(`${role.name}: Role file credits its Upstream`, async () => {
    const file = await roleFile(role);
    const { name, url, license } = role.upstream;
    assert.match(file, new RegExp(`\\[${escape(name)}\\]\\(${escape(url)}\\) \\(${escape(license)}\\)`));
  });

  test(`${role.name}: Role file scopes the Teammate to its own skills plus the Base rule`, async () => {
    const file = await roleFile(role);
    assert.ok(role.skills.length > 0);
    for (const skill of role.skills) assert.ok(file.includes(`\`${skill}\``), skill);
    assert.match(file, /`ponytail:ponytail`/);
    assert.match(file, /Ignore every other skill/);
  });
}

test('only the Builder, Planner and Gatekeeper may edit files', async () => {
  const editors = roles.filter((r) => r.edits !== 'none').map((r) => `${r.name}: ${r.edits}`).sort();
  assert.deepEqual(editors, ['Builder: source and tests', 'Gatekeeper: docs and changelog', 'Planner: plans']);
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
  assert.equal((await generate({ rolesDir, outDir: empty, check: true })).length, roles.length);
  assert.deepEqual(await readdir(empty), []);
});

test('committed Role files are up to date', async () => {
  assert.deepEqual(await generate({ rolesDir, outDir: agentsDir, check: true }), []);
});
