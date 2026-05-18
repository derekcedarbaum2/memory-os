// vault router — Knowledge Router lookups + validation.
// The router is MEMORY.md (one line per pointer: `- [Title](file.md) — hook`)
// plus a reference_knowledge_router.md memory file.

import { existsSync, readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { MEMORY_INDEX, MEMORY_DIR } from '../lib/config.js';
import { emit, fail } from '../lib/output.js';

const HELP = `vault router — Knowledge Router lookups + validation

Usage:
  vault router lookup <query>     Find pointers matching <query> (case-insensitive)
  vault router list                List all pointers
  vault router check               Validate every pointer file exists
  vault router --help
`;

const POINTER_RE = /^- \[([^\]]+)\]\(([^)]+)\)\s*[—\-–]\s*(.+)$/;

export async function dispatchRouter(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'lookup':
      await lookup(rest);
      break;
    case 'list':
      await listAll(rest);
      break;
    case 'check':
      await check(rest);
      break;
    default:
      fail(`unknown router subcommand: ${sub}`);
  }
}

function loadPointers() {
  if (!MEMORY_INDEX) {
    fail(`MEMORY.md not found — no project memory directory under ~/.claude/projects/.\nInstall ai-knowledge-system first: https://github.com/derekcedarbaum2/ai-knowledge-system\nOr set VAULT_MEMORY_DIR to point at your memory directory.`);
  }
  if (!existsSync(MEMORY_INDEX)) {
    fail(`MEMORY.md not found at ${MEMORY_INDEX}`);
  }
  const content = readFileSync(MEMORY_INDEX, 'utf8');
  const pointers = [];
  for (const line of content.split('\n')) {
    const m = line.match(POINTER_RE);
    if (m) {
      pointers.push({ title: m[1], file: m[2], hook: m[3].trim() });
    }
  }
  return pointers;
}

async function lookup(args) {
  const query = args.find(a => !a.startsWith('--'));
  if (!query) fail('vault router lookup requires a query');
  const q = query.toLowerCase();
  const pointers = loadPointers();
  const matches = pointers.filter(p =>
    p.title.toLowerCase().includes(q) || p.hook.toLowerCase().includes(q)
  );
  emit({ query, count: matches.length, matches }, args);
}

async function listAll(args) {
  const pointers = loadPointers();
  emit({ count: pointers.length, pointers }, args);
}

async function check(args) {
  const pointers = loadPointers();
  const memDir = MEMORY_DIR;
  const broken = [];
  const ok = [];
  for (const p of pointers) {
    const target = p.file.startsWith('/') ? p.file : resolve(memDir, p.file);
    if (existsSync(target)) {
      ok.push({ ...p, resolved: target });
    } else {
      broken.push({ ...p, resolved: target, reason: 'file not found' });
    }
  }
  const result = { total: pointers.length, ok: ok.length, broken: broken.length, broken_pointers: broken };
  emit(result, args);
  if (broken.length > 0) process.exit(1);
}
