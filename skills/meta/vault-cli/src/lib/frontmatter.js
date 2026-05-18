// YAML frontmatter parser. Lightweight — no external deps. Handles the
// vault-conventions schema: title, type, status, classification, created,
// updated, author, tags. Optional: product, program, related, source, owner, due.

import { readFileSync, writeFileSync } from 'node:fs';

const FENCE = '---';

export function parseFrontmatter(content) {
  const lines = content.split('\n');
  if (lines[0] !== FENCE) return { frontmatter: null, body: content };

  let endIdx = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i] === FENCE) {
      endIdx = i;
      break;
    }
  }
  if (endIdx === -1) return { frontmatter: null, body: content };

  const yaml = lines.slice(1, endIdx).join('\n');
  const body = lines.slice(endIdx + 1).join('\n');
  return { frontmatter: parseYaml(yaml), body };
}

function parseYaml(yaml) {
  const result = {};
  const lines = yaml.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();
    // Strip wrapping quotes
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    // Inline arrays: tags: [a, b, c]
    if (value.startsWith('[') && value.endsWith(']')) {
      const inner = value.slice(1, -1).trim();
      value = inner ? inner.split(',').map(s => s.trim().replace(/^["']|["']$/g, '')) : [];
    }
    result[key] = value;
  }
  return result;
}

export function serializeFrontmatter(fm) {
  const lines = [FENCE];
  const order = ['title', 'type', 'status', 'classification', 'created', 'updated', 'author', 'tags',
                 'product', 'program', 'related', 'source', 'owner', 'due'];
  const seen = new Set();
  for (const key of order) {
    if (key in fm) {
      lines.push(serializePair(key, fm[key]));
      seen.add(key);
    }
  }
  for (const key of Object.keys(fm)) {
    if (!seen.has(key)) {
      lines.push(serializePair(key, fm[key]));
    }
  }
  lines.push(FENCE);
  return lines.join('\n');
}

function serializePair(key, value) {
  if (Array.isArray(value)) {
    return `${key}: [${value.map(v => typeof v === 'string' && v.includes(' ') ? `"${v}"` : v).join(', ')}]`;
  }
  if (typeof value === 'string' && /[:#]/.test(value)) {
    return `${key}: "${value.replace(/"/g, '\\"')}"`;
  }
  return `${key}: ${value}`;
}

export const REQUIRED_FIELDS = ['title', 'type', 'status', 'classification', 'created', 'updated', 'author'];

export function validateFrontmatter(fm) {
  const issues = [];
  if (!fm) {
    return { valid: false, issues: ['no frontmatter block'] };
  }
  for (const field of REQUIRED_FIELDS) {
    if (!(field in fm) || fm[field] === '' || fm[field] == null) {
      issues.push(`missing required field: ${field}`);
    }
  }
  // tags is required structurally even if empty
  if (!('tags' in fm)) {
    issues.push('missing required field: tags (use empty array [])');
  }
  return { valid: issues.length === 0, issues };
}

export function readWithFrontmatter(path) {
  const content = readFileSync(path, 'utf8');
  return { ...parseFrontmatter(content), path };
}

export function writeWithFrontmatter(path, frontmatter, body) {
  const fm = serializeFrontmatter(frontmatter);
  writeFileSync(path, `${fm}\n${body}`);
}
