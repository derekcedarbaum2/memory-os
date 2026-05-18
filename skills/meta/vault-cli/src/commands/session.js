// vault session — session archive operations.

import { spawn } from 'node:child_process';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { HOOK_ARCHIVE_SESSION, SESSIONS_DIR } from '../lib/config.js';
import { emit, info, fail } from '../lib/output.js';

const HELP = `vault session — session archive operations

Usage:
  vault session archive [--from-stdin]    Wrap archive-session.sh (typical: piped JSON from SessionEnd)
  vault session list [--limit N]           List recent session archives
  vault session --help
`;

export async function dispatchSession(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'archive':
      await archiveSession(rest);
      break;
    case 'list':
      await listSessions(rest);
      break;
    default:
      fail(`unknown session subcommand: ${sub}`);
  }
}

async function archiveSession() {
  if (!existsSync(HOOK_ARCHIVE_SESSION)) {
    fail(`hook script not found: ${HOOK_ARCHIVE_SESSION}`);
  }
  await new Promise((resolveP, rejectP) => {
    info(`executing: ${HOOK_ARCHIVE_SESSION}`);
    const child = spawn(HOOK_ARCHIVE_SESSION, [], { stdio: 'inherit' });
    child.on('exit', code => code === 0 ? resolveP() : rejectP(new Error(`hook exited with code ${code}`)));
    child.on('error', rejectP);
  });
}

async function listSessions(args) {
  if (!existsSync(SESSIONS_DIR)) {
    emit({ count: 0, sessions: [] }, args);
    return;
  }
  const limitIdx = args.indexOf('--limit');
  const limit = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : 20;
  const files = readdirSync(SESSIONS_DIR)
    .filter(f => f.endsWith('.md') && !['Concepts', 'Indexes'].includes(f))
    .map(f => {
      const path = resolve(SESSIONS_DIR, f);
      try {
        const st = statSync(path);
        return { name: f, path, mtime: st.mtime.toISOString(), size: st.size };
      } catch {
        return null;
      }
    })
    .filter(Boolean)
    .sort((a, b) => b.mtime.localeCompare(a.mtime))
    .slice(0, limit);
  emit({ count: files.length, sessions: files }, args);
}
