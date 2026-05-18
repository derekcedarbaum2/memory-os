// vault distill — wraps the existing auto-distill-readwise.sh runner.
// State-file ops are native (read/write JSON atomically).

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { HOOK_AUTO_DISTILL, DISTILL_STATE } from '../lib/config.js';
import { readState, writeState } from '../lib/state.js';
import { emit, info, fail } from '../lib/output.js';

const HELP = `vault distill — distill external content (Readwise) into playbooks

Usage:
  vault distill run [--dry-run] [--backfill]    Run the daily distill cycle
  vault distill ingest <file> [--dry-run]       Distill one specific file
  vault distill state get                        Print state JSON
  vault distill state mark-processed <file>      Mark a file as already processed
  vault distill --help                           Print this help

The 'run' and 'ingest' commands wrap ~/.claude/hooks/auto-distill-readwise.sh.
State commands are native.
`;

export async function dispatchDistill(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'run':
      await runDistill(rest);
      break;
    case 'ingest':
      await ingestFile(rest);
      break;
    case 'state':
      await stateCmd(rest);
      break;
    default:
      fail(`unknown distill subcommand: ${sub}\n\n${HELP}`);
  }
}

async function runDistill(args) {
  if (!existsSync(HOOK_AUTO_DISTILL)) {
    fail(`hook script not found: ${HOOK_AUTO_DISTILL}\nThis CLI v0.1 wraps existing hook scripts; install vault-conventions first or implement natively.`);
  }
  const hookArgs = [];
  if (args.includes('--dry-run')) hookArgs.push('--dry-run');
  if (args.includes('--backfill')) hookArgs.push('--backfill');
  await execHook(HOOK_AUTO_DISTILL, hookArgs);
}

async function ingestFile(args) {
  const file = args.find(a => !a.startsWith('--'));
  if (!file) fail('vault distill ingest requires a file path');
  if (!existsSync(file)) fail(`file not found: ${file}`);
  if (!existsSync(HOOK_AUTO_DISTILL)) {
    fail(`hook script not found: ${HOOK_AUTO_DISTILL}`);
  }
  const hookArgs = ['--file', file];
  if (args.includes('--dry-run')) hookArgs.push('--dry-run');
  await execHook(HOOK_AUTO_DISTILL, hookArgs);
}

async function stateCmd(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(`vault distill state — distill state-file operations

Usage:
  vault distill state get                       Print full state JSON
  vault distill state mark-processed <file>    Mark a file as processed
`);
    return;
  }
  const sub = args[0];
  if (sub === 'get') {
    const state = readState(DISTILL_STATE, { processed: {}, runs: [] });
    emit(state, args);
  } else if (sub === 'mark-processed') {
    const file = args[1];
    if (!file) fail('vault distill state mark-processed requires a file path');
    const state = readState(DISTILL_STATE, { processed: {}, runs: [] });
    state.processed = state.processed || {};
    state.processed[file] = { processed_at: new Date().toISOString(), via: 'vault-cli' };
    writeState(DISTILL_STATE, state);
    emit({ ok: true, file, marked: state.processed[file] }, args);
  } else {
    fail(`unknown distill state subcommand: ${sub}`);
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
