// vault voice-memo — voice memo file ops.

import { existsSync, readdirSync, statSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { VOICE_MEMOS_DIR } from '../lib/config.js';
import { emit, fail } from '../lib/output.js';

const HELP = `vault voice-memo — voice memo file operations

Usage:
  vault voice-memo list [--limit N] [--unprocessed]    List voice memos
  vault voice-memo get <slug>                           Print one voice memo's content + processed status
  vault voice-memo --help
`;

export async function dispatchVoiceMemo(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'list':
      await listMemos(rest);
      break;
    case 'get':
      await getMemo(rest);
      break;
    default:
      fail(`unknown voice-memo subcommand: ${sub}`);
  }
}

async function listMemos(args) {
  if (!existsSync(VOICE_MEMOS_DIR)) {
    emit({ count: 0, memos: [] }, args);
    return;
  }
  const limitIdx = args.indexOf('--limit');
  const limit = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : 50;
  const onlyUnprocessed = args.includes('--unprocessed');
  const allFiles = readdirSync(VOICE_MEMOS_DIR);
  const memos = allFiles
    .filter(f => f.endsWith('.md') && !f.endsWith('.actions.md'))
    .map(f => {
      const path = resolve(VOICE_MEMOS_DIR, f);
      const actionsPath = path.replace(/\.md$/, '.actions.md');
      const processed = existsSync(actionsPath);
      try {
        const st = statSync(path);
        return { name: f, path, mtime: st.mtime.toISOString(), size: st.size, processed };
      } catch {
        return null;
      }
    })
    .filter(Boolean)
    .filter(m => onlyUnprocessed ? !m.processed : true)
    .sort((a, b) => b.mtime.localeCompare(a.mtime))
    .slice(0, limit);
  emit({ count: memos.length, memos }, args);
}

async function getMemo(args) {
  const slug = args[0];
  if (!slug) fail('vault voice-memo get requires a slug or filename');
  const path = slug.includes('/') ? slug : resolve(VOICE_MEMOS_DIR, slug.endsWith('.md') ? slug : `${slug}.md`);
  if (!existsSync(path)) fail(`memo not found: ${path}`);
  const content = readFileSync(path, 'utf8');
  const actionsPath = path.replace(/\.md$/, '.actions.md');
  const processed = existsSync(actionsPath);
  const actions = processed ? readFileSync(actionsPath, 'utf8') : null;
  emit({ path, processed, content, actions }, args);
}
