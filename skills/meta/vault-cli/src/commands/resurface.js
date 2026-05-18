// vault resurface — wraps learnings-resurface.sh; state ops are native.

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { HOOK_RESURFACE, RESURFACE_STATE } from '../lib/config.js';
import { readState, writeState } from '../lib/state.js';
import { emit, info, fail } from '../lib/output.js';

const HELP = `vault resurface — cluster + classify accumulated interaction memory

Usage:
  vault resurface run [--dry-run] [--window N]   Run a resurface pass (default window 90d)
  vault resurface state get                       Print state JSON
  vault resurface state last-run                  Print metadata for the most recent run
  vault resurface --help                          Print this help

The 'run' command wraps ~/.claude/hooks/learnings-resurface.sh.
`;

export async function dispatchResurface(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'run':
      await runResurface(rest);
      break;
    case 'state':
      await stateCmd(rest);
      break;
    default:
      fail(`unknown resurface subcommand: ${sub}`);
  }
}

async function runResurface(args) {
  if (!existsSync(HOOK_RESURFACE)) {
    fail(`hook script not found: ${HOOK_RESURFACE}`);
  }
  const hookArgs = [];
  if (args.includes('--dry-run')) hookArgs.push('--dry-run');
  const winIdx = args.indexOf('--window');
  if (winIdx !== -1 && args[winIdx + 1]) hookArgs.push('--window', args[winIdx + 1]);
  await execHook(HOOK_RESURFACE, hookArgs);
}

async function stateCmd(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(`vault resurface state — resurface state-file operations

Usage:
  vault resurface state get          Print full state JSON
  vault resurface state last-run     Print most recent run metadata
`);
    return;
  }
  const sub = args[0];
  const state = readState(RESURFACE_STATE, { runs: {}, cluster_fingerprints: {} });
  if (sub === 'get') {
    emit(state, args);
  } else if (sub === 'last-run') {
    const runIds = Object.keys(state.runs || {}).sort();
    const last = runIds.at(-1);
    emit(last ? { run_id: last, ...state.runs[last] } : { ok: false, reason: 'no runs recorded' }, args);
  } else {
    fail(`unknown resurface state subcommand: ${sub}`);
  }
}

function execHook(path, args) {
  return new Promise((resolve, reject) => {
    info(`executing: ${path} ${args.join(' ')}`);
    const child = spawn(path, args, { stdio: 'inherit' });
    child.on('exit', code => {
      if (code === 0) resolve();
      else reject(new Error(`hook exited with code ${code}`));
    });
    child.on('error', reject);
  });
}
