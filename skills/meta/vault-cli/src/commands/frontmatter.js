// vault frontmatter — YAML frontmatter audit + backfill.

import { readdirSync, statSync, existsSync } from 'node:fs';
import { resolve, basename } from 'node:path';
import { VAULT_PATH } from '../lib/config.js';
import { readWithFrontmatter, writeWithFrontmatter, validateFrontmatter, REQUIRED_FIELDS } from '../lib/frontmatter.js';
import { emit, fail, info } from '../lib/output.js';

const HELP = `vault frontmatter — YAML frontmatter audit + backfill

Usage:
  vault frontmatter check <path>             Validate one file
  vault frontmatter audit [--path <dir>]     Scan vault for files missing/malformed frontmatter
  vault frontmatter add <path> [--type <t>]  Backfill frontmatter on a file (interactive guesses)
  vault frontmatter --help

Excluded from audit by default: _archive/, _attachments/, raw-sources/, Reading/.
`;

const SKIP_DIRS = new Set(['_archive', '_attachments', 'raw-sources', 'Reading', 'node_modules', '.git', '.obsidian']);

export async function dispatchFrontmatter(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'check':
      await checkOne(rest);
      break;
    case 'audit':
      await audit(rest);
      break;
    case 'add':
      await addOne(rest);
      break;
    default:
      fail(`unknown frontmatter subcommand: ${sub}`);
  }
}

async function checkOne(args) {
  const path = args[0];
  if (!path) fail('vault frontmatter check requires a path');
  if (!existsSync(path)) fail(`file not found: ${path}`);
  const { frontmatter } = readWithFrontmatter(path);
  const result = validateFrontmatter(frontmatter);
  emit({ path, ...result, frontmatter }, args);
  if (!result.valid) process.exit(1);
}

async function audit(args) {
  const pathIdx = args.indexOf('--path');
  const root = pathIdx !== -1 ? args[pathIdx + 1] : VAULT_PATH;
  if (!existsSync(root)) fail(`path not found: ${root}`);

  const issues = [];
  const checked = [];

  function walk(dir) {
    let entries;
    try {
      entries = readdirSync(dir);
    } catch {
      return;
    }
    for (const name of entries) {
      if (SKIP_DIRS.has(name)) continue;
      if (name.startsWith('.')) continue;
      const path = resolve(dir, name);
      let st;
      try {
        st = statSync(path);
      } catch {
        continue;
      }
      if (st.isDirectory()) {
        walk(path);
      } else if (st.isFile() && name.endsWith('.md')) {
        try {
          const { frontmatter } = readWithFrontmatter(path);
          const result = validateFrontmatter(frontmatter);
          checked.push(path);
          if (!result.valid) {
            issues.push({ path, issues: result.issues });
          }
        } catch (err) {
          issues.push({ path, issues: [`parse error: ${err.message}`] });
        }
      }
    }
  }

  walk(root);
  emit({ root, files_checked: checked.length, files_with_issues: issues.length, issues }, args);
  if (issues.length > 0) process.exit(1);
}

async function addOne(args) {
  const path = args[0];
  if (!path) fail('vault frontmatter add requires a path');
  if (!existsSync(path)) fail(`file not found: ${path}`);
  const typeIdx = args.indexOf('--type');
  const type = typeIdx !== -1 ? args[typeIdx + 1] : 'reference';

  const { frontmatter, body } = readWithFrontmatter(path);
  const today = new Date().toISOString().slice(0, 10);
  const next = {
    title: frontmatter?.title ?? basename(path).replace(/\.md$/, '').replace(/-/g, ' '),
    type: frontmatter?.type ?? type,
    status: frontmatter?.status ?? 'draft',
    classification: frontmatter?.classification ?? 'internal',
    created: frontmatter?.created ?? today,
    updated: today,
    author: frontmatter?.author ?? 'Derek Cedarbaum',
    tags: frontmatter?.tags ?? [],
    ...frontmatter,
  };
  // Override updated even if frontmatter had one (we just touched it).
  next.updated = today;

  writeWithFrontmatter(path, next, body);
  info(`backfilled frontmatter on ${path}`);
  emit({ ok: true, path, frontmatter: next, required_fields: REQUIRED_FIELDS }, args);
}
