// Operator-specific config. Resolved from environment variables with auto-discovery
// fallbacks so the CLI works on any Claude Code setup with zero configuration.

import { homedir } from 'node:os';
import { resolve } from 'node:path';
import { existsSync, readdirSync, statSync } from 'node:fs';

const HOME = homedir();

// VAULT_PATH: env var → auto-discover common locations → undefined.
function discoverVaultPath() {
  if (process.env.VAULT_PATH) return process.env.VAULT_PATH;
  const candidates = [
    // Obsidian on macOS with iCloud sync
    resolve(HOME, 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault'),
    // Common explicit locations
    resolve(HOME, 'Documents/Vault'),
    resolve(HOME, 'vault'),
    resolve(HOME, 'Vault'),
    resolve(HOME, 'notes'),
  ];
  for (const path of candidates) {
    if (existsSync(path) && existsSync(resolve(path, 'CLAUDE.md'))) return path;
  }
  // Last resort: first matching path that exists, even without CLAUDE.md
  for (const path of candidates) {
    if (existsSync(path)) return path;
  }
  return null;
}

export const VAULT_PATH = discoverVaultPath();

export const CLAUDE_HOME = process.env.CLAUDE_HOME || resolve(HOME, '.claude');
export const HOOKS_DIR = resolve(CLAUDE_HOME, 'hooks');
export const SKILLS_DIR = resolve(CLAUDE_HOME, 'skills');
export const STATE_DIR = resolve(CLAUDE_HOME, 'state');

// Memory layout: env var → auto-discover the active project memory dir.
// Claude Code names project dirs based on cwd-derived ids (e.g. -Users-jane).
// Pick the most-recently-modified one with a MEMORY.md.
function discoverMemoryDir() {
  if (process.env.VAULT_MEMORY_DIR) return process.env.VAULT_MEMORY_DIR;
  const projectsDir = resolve(CLAUDE_HOME, 'projects');
  if (!existsSync(projectsDir)) return null;
  let best = null;
  let bestMtime = 0;
  for (const name of readdirSync(projectsDir)) {
    const memDir = resolve(projectsDir, name, 'memory');
    const memIndex = resolve(memDir, 'MEMORY.md');
    if (existsSync(memIndex)) {
      try {
        const mtime = statSync(memIndex).mtimeMs;
        if (mtime > bestMtime) {
          best = memDir;
          bestMtime = mtime;
        }
      } catch {}
    }
  }
  return best;
}

export const MEMORY_DIR = discoverMemoryDir();
export const MEMORY_INDEX = MEMORY_DIR ? resolve(MEMORY_DIR, 'MEMORY.md') : null;

// Vault sub-paths.
export const VAULT_LOG = resolve(VAULT_PATH, 'log.md');
export const SESSIONS_DIR = resolve(VAULT_PATH, 'AI Toolkit/CC Chat History');
export const VOICE_MEMOS_DIR = resolve(VAULT_PATH, 'Voice Memos');
export const PLAYBOOKS_INDEX = resolve(VAULT_PATH, 'Playbooks-Index.md');
export const TODAY_FILE = resolve(VAULT_PATH, 'Today.md');

// State files.
export const DISTILL_STATE = resolve(STATE_DIR, 'distilled-readwise.json');
export const RESURFACE_STATE = resolve(STATE_DIR, 'learnings-resurface.json');

// Hook scripts (existing — wrapped by v0.1, replaced incrementally).
export const HOOK_AUTO_DISTILL = resolve(HOOKS_DIR, 'auto-distill-readwise.sh');
export const HOOK_RESURFACE = resolve(HOOKS_DIR, 'learnings-resurface.sh');
export const HOOK_ARCHIVE_SESSION = resolve(HOOKS_DIR, 'archive-session.sh');
export const HOOK_GENERATE_TODAY = resolve(HOOKS_DIR, 'generate-today.sh');

// Detect non-TTY for default JSON output.
export const IS_TTY = process.stdout.isTTY === true;
