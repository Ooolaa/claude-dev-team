// Scores a finished working tree against one benchmark task. No LLM: Traps are
// checked by changed-file globs and by pytest results; tests run in Docker.
import { execFileSync, spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { cp, mkdtemp, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, matchesGlob } from 'node:path';
import { fileURLToPath } from 'node:url';

const scorerDir = fileURLToPath(new URL('.', import.meta.url));
const HIDDEN = 'tests/hidden';

const git = (cwd, ...args) => execFileSync('git', args, { cwd, encoding: 'utf8' });

function changedFiles(tree, commit) {
  const lines = git(tree, 'diff', '--name-only', commit) + git(tree, 'ls-files', '--others', '--exclude-standard');
  return lines.split('\n').filter(Boolean);
}

// junit.xml → Map of "tests/path.py::test_name" → passed (all parametrized cases must pass).
function parseJunit(xml) {
  const results = new Map();
  for (const [, attrs, body = ''] of xml.matchAll(/<testcase\b([^>]*?)(?:\/>|>([\s\S]*?)<\/testcase>)/g)) {
    const attr = (k) => attrs.match(new RegExp(`\\b${k}="([^"]*)"`))?.[1] ?? '';
    const key = `${attr('classname').replaceAll('.', '/')}.py::${attr('name').replace(/\[.*$/, '')}`;
    const passed = !/<(failure|error|skipped)\b/.test(body);
    results.set(key, (results.get(key) ?? true) && passed);
  }
  return results;
}

function runPytest(work, files) {
  const compose = ['compose', '-f', join(scorerDir, 'compose.yml'), '-p', `rolecall-${randomUUID().slice(0, 8)}`];
  const env = { ...process.env, WORK: work, TESTS: files.join(' ') };
  // Test failures exit non-zero, so the junit file is the source of truth. No junit file means
  // pytest never ran (Docker down, install or migration failed): raise rather than score it.
  const run = spawnSync('docker', [...compose, 'run', '--rm', 'tests'], { env, encoding: 'utf8' });
  spawnSync('docker', [...compose, 'down', '-v'], { env, stdio: 'ignore' });
  return readFile(join(work, 'junit.xml'), 'utf8').then(parseJunit, () => {
    const output = `${run.error ?? ''}${run.stdout ?? ''}${run.stderr ?? ''}`.slice(-2000);
    throw new Error(`pytest produced no results (docker exit ${run.status}):\n${output}`);
  });
}

const testNames = async (file) =>
  [...(await readFile(file, 'utf8')).matchAll(/^def (test_\w+)/gm)].map((m) => m[1]);

/**
 * @param {{ taskDir: string, tree: string }} args  tree: a git checkout of the pinned template with the agent's changes
 * @returns {Promise<{ tests: Record<string, 'pass'|'fail'>, traps: Record<string, 'tripped'|'clear'> }>}
 */
export async function score({ taskDir, tree }) {
  const task = JSON.parse(await readFile(join(taskDir, 'task.json'), 'utf8'));
  const { commit } = JSON.parse(await readFile(join(scorerDir, '..', 'template.json'), 'utf8'));
  const changed = changedFiles(tree, commit);

  const work = await mkdtemp(join(tmpdir(), 'rolecall-score-'));
  try {
    await cp(tree, work, { recursive: true, filter: (src) => !/[\\/](node_modules|\.venv)$/.test(src) });
    // Score against the template's own tests as pinned, plus the hidden ones; never the agent's edits to them.
    git(work, 'checkout', commit, '--', 'backend/tests');
    await cp(join(taskDir, 'hidden'), join(work, 'backend', HIDDEN), { recursive: true });
    await writeFile(join(work, 'backend', HIDDEN, '__init__.py'), '');

    const hiddenFiles = (await readdir(join(taskDir, 'hidden'))).filter((f) => /^test_.*\.py$/.test(f)).map((f) => `${HIDDEN}/${f}`);
    const trapPrefixes = task.traps.flatMap((t) => t.tests ?? []);
    const files = [...new Set([...hiddenFiles, ...trapPrefixes.map((p) => p.split('::')[0])])];

    const expected = [];
    for (const file of files) for (const name of await testNames(join(work, 'backend', file))) expected.push(`${file}::${name}`);
    const results = await runPytest(work, files);
    const passed = (key) => results.get(key) === true;
    const under = (prefix) => expected.filter((k) => k === prefix || k.startsWith(`${prefix}::`));

    const tests = {};
    for (const key of expected) {
      if (hiddenFiles.some((f) => key.startsWith(`${f}::`)) && !trapPrefixes.some((p) => under(p).includes(key))) {
        tests[key] = passed(key) ? 'pass' : 'fail';
      }
    }
    const traps = {};
    for (const trap of task.traps) {
      const failedTest = (trap.tests ?? []).some((p) => under(p).some((k) => !passed(k)));
      const touched = (trap.changed ?? []).some((glob) => changed.some((f) => matchesGlob(f, glob)));
      traps[trap.id] = failedTest || touched ? 'tripped' : 'clear';
    }
    return { tests, traps };
  } finally {
    await rm(work, { recursive: true, force: true });
  }
}
