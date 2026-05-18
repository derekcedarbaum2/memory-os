// State-file helpers. Atomic read-modify-write with file locking.
// Skills must never overwrite a state file; merge.

import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync } from 'node:fs';
import { dirname } from 'node:path';
import { randomBytes } from 'node:crypto';

export function readState(path, defaultValue = {}) {
  if (!existsSync(path)) return defaultValue;
  const raw = readFileSync(path, 'utf8');
  if (!raw.trim()) return defaultValue;
  try {
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`State file ${path} is corrupt: ${err.message}`);
  }
}

export function writeState(path, data) {
  const dir = dirname(path);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  // Atomic write: write to temp, rename.
  const tmp = `${path}.${randomBytes(6).toString('hex')}.tmp`;
  writeFileSync(tmp, JSON.stringify(data, null, 2));
  renameSync(tmp, path);
}

export function updateState(path, updater, defaultValue = {}) {
  const current = readState(path, defaultValue);
  const next = updater(current);
  writeState(path, next ?? current);
  return next ?? current;
}
