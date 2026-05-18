// vault learnings — append-only writes to _learnings.md.

import { readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { VAULT_PATH } from '../lib/config.js';
import { emit, fail, info } from '../lib/output.js';

const HELP = `vault learnings — append-only writes to _learnings.md

Usage:
  vault learnings append <venture-folder> <entry>            Append to ## Learnings section
  vault learnings decision <venture-folder> <decision>       Append to ## Key Decisions
  vault learnings open-thread <venture-folder> <question>    Append to ## Open Threads
  vault learnings --help

The venture folder is relative to the vault root (e.g., 'Ideas/Bastion' or 'Work/Unlikely Labs').
The CLI never rewrites or deletes existing entries — append-only is enforced.
`;

export async function dispatchLearnings(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'append':
      await appendSection(rest, '## Learnings', 'Learning');
      break;
    case 'decision':
      await appendSection(rest, '## Key Decisions', 'Decision');
      break;
    case 'open-thread':
      await appendSection(rest, '## Open Threads', 'Open thread');
      break;
    default:
      fail(`unknown learnings subcommand: ${sub}`);
  }
}

async function appendSection(args, sectionHeader, label) {
  const venture = args[0];
  const entry = args.slice(1).join(' ').trim();
  if (!venture) fail(`vault learnings ${args[-1] || ''} requires a venture folder`);
  if (!entry) fail(`vault learnings requires entry text`);

  const ventureDir = resolve(VAULT_PATH, venture);
  if (!existsSync(ventureDir) || !statSync(ventureDir).isDirectory()) {
    fail(`venture folder not found: ${ventureDir}`);
  }
  const learningsPath = resolve(ventureDir, '_learnings.md');
  if (!existsSync(learningsPath)) {
    fail(`_learnings.md not found at ${learningsPath}\nCreate scaffolding first.`);
  }

  const content = readFileSync(learningsPath, 'utf8');
  const today = new Date().toISOString().slice(0, 10);
  const newLine = `- ${entry} *(${today})*`;

  const lines = content.split('\n');
  // Find the section header
  let headerIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === sectionHeader) {
      headerIdx = i;
      break;
    }
  }
  if (headerIdx === -1) {
    fail(`section "${sectionHeader}" not found in ${learningsPath}\nAdd the section heading first.`);
  }

  // Insert at the end of that section (before the next ## or EOF).
  let insertIdx = lines.length;
  for (let i = headerIdx + 1; i < lines.length; i++) {
    if (/^##\s/.test(lines[i])) {
      insertIdx = i;
      break;
    }
  }
  // Skip blank lines backwards to keep cleanliness.
  while (insertIdx > headerIdx + 1 && lines[insertIdx - 1].trim() === '') {
    insertIdx--;
  }

  const before = lines.slice(0, insertIdx);
  const after = lines.slice(insertIdx);
  const next = [...before, newLine, ...after].join('\n');
  writeFileSync(learningsPath, next);

  info(`appended ${label} to ${learningsPath}`);
  emit({ ok: true, path: learningsPath, section: sectionHeader, entry: newLine }, args);
}
