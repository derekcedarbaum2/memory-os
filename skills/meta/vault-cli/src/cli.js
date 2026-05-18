#!/usr/bin/env node
// vault — deterministic CLI primitives for a Claude Code + Obsidian vault setup.
//
// Skills call this CLI for deterministic work (file ops, state-file mutations,
// router lookups, frontmatter audits). The LLM does only judgment.
//
// Sub-commands are dispatched to src/commands/<group>.js modules.

import { argv, exit } from 'node:process';
import { dispatchDistill } from './commands/distill.js';
import { dispatchResurface } from './commands/resurface.js';
import { dispatchSession } from './commands/session.js';
import { dispatchVoiceMemo } from './commands/voice-memo.js';
import { dispatchRouter } from './commands/router.js';
import { dispatchFrontmatter } from './commands/frontmatter.js';
import { dispatchLearnings } from './commands/learnings.js';
import { dispatchSkill } from './commands/skill.js';
import { dispatchState } from './commands/state.js';
import { dispatchToday } from './commands/today.js';
import { printVersion } from './lib/version.js';

const HELP = `vault — deterministic CLI for a Claude Code + Obsidian vault setup

Usage: vault <group> <command> [args...]

Groups:
  distill        Distill external content (Readwise) into playbooks
  resurface     Cluster + classify accumulated interaction memory
  session       Session archive operations
  voice-memo    Voice memo processing
  router        Knowledge Router lookups + validation
  frontmatter   YAML frontmatter audit + backfill
  learnings     Append-only writes to _learnings.md
  skill         Scaffold + check Claude Code skills
  state         Read/write skill state files
  today         Ephemeral working-memory artifact (Vault/Today.md)

Common:
  vault --version        Print version
  vault --help           Print this help
  vault <group> --help   Help for a specific group

Most commands emit JSON on --json or when stdout is non-TTY.

See README.md and AGENTS.md for full documentation.
`;

const args = argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  process.stdout.write(HELP);
  exit(0);
}

if (args[0] === '--version' || args[0] === '-v') {
  printVersion();
  exit(0);
}

const group = args[0];
const rest = args.slice(1);

try {
  switch (group) {
    case 'distill':
      await dispatchDistill(rest);
      break;
    case 'resurface':
      await dispatchResurface(rest);
      break;
    case 'session':
      await dispatchSession(rest);
      break;
    case 'voice-memo':
      await dispatchVoiceMemo(rest);
      break;
    case 'router':
      await dispatchRouter(rest);
      break;
    case 'frontmatter':
      await dispatchFrontmatter(rest);
      break;
    case 'learnings':
      await dispatchLearnings(rest);
      break;
    case 'skill':
      await dispatchSkill(rest);
      break;
    case 'state':
      await dispatchState(rest);
      break;
    case 'today':
      await dispatchToday(rest);
      break;
    default:
      process.stderr.write(`Unknown command group: ${group}\n\n`);
      process.stdout.write(HELP);
      exit(1);
  }
} catch (err) {
  process.stderr.write(`vault: ${err.message}\n`);
  if (process.env.VAULT_DEBUG) {
    process.stderr.write(err.stack + '\n');
  }
  exit(1);
}
