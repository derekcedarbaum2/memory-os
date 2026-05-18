// vault state — list / inspect skill state files.

import { existsSync, readdirSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { STATE_DIR } from '../lib/config.js';
import { readState } from '../lib/state.js';
import { emit, fail } from '../lib/output.js';

const HELP = `vault state — list / inspect skill state files

Usage:
  vault state list             List all state files
  vault state get <name>       Print one state file's content (without .json suffix)
  vault state --help
`;

export async function dispatchState(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'list':
      await listAll(rest);
      break;
    case 'get':
      await getOne(rest);
      break;
    default:
      fail(`unknown state subcommand: ${sub}`);
  }
}

async function listAll(args) {
  if (!existsSync(STATE_DIR)) {
    emit({ count: 0, files: [] }, args);
    return;
  }
  const files = readdirSync(STATE_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => {
      const path = resolve(STATE_DIR, f);
      try {
        const st = statSync(path);
        return { name: f.replace(/\.json$/, ''), path, mtime: st.mtime.toISOString(), size: st.size };
      } catch {
        return null;
      }
    })
    .filter(Boolean);
  emit({ count: files.length, files }, args);
}

async function getOne(args) {
  const name = args[0];
  if (!name) fail('vault state get requires a state file name');
  const path = resolve(STATE_DIR, name.endsWith('.json') ? name : `${name}.json`);
  if (!existsSync(path)) fail(`state file not found: ${path}`);
  const content = readState(path, null);
  emit({ path, content }, args);
}
