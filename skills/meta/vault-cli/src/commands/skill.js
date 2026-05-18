// vault skill — scaffold + check Claude Code skills.

import { existsSync, mkdirSync, writeFileSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { resolve, basename } from 'node:path';
import { SKILLS_DIR } from '../lib/config.js';
import { emit, fail, info } from '../lib/output.js';

const HELP = `vault skill — scaffold + check Claude Code skills

Usage:
  vault skill new <name> [--description "..."] [--model opus|sonnet]    Scaffold a new skill
  vault skill check <name>                                              Validate skill conformance
  vault skill list                                                       List installed skills
  vault skill --help

Conformance rules (per claude-code-setup skill architecture):
- SKILL.md exists with frontmatter (name, description, version)
- SKILL.md is < 500 lines
- examples/bad/ANTIPATTERNS.md exists and is non-empty (anchored examples + hard gates rule)
- All file references in SKILL.md resolve
`;

const TEMPLATE_SKILL_MD = (name, description, model) => `---
name: ${name}
description: ${description}
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]${model ? `\nmodel: ${model}` : ''}
---

# ${titleCase(name)}

[One-paragraph description of what this skill does and when to fire.]

## When to Use This Skill

Activate when user:
- [trigger phrase or scenario]
- [trigger phrase or scenario]

Do NOT activate for:
- [excluded scenario] (use \`/other-skill\` instead)

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output

[What the skill produces and where it goes.]

## Anti-patterns (avoid these)

See \`examples/bad/ANTIPATTERNS.md\` for the full list.
`;

const TEMPLATE_ANTIPATTERNS = (name) => `# ${titleCase(name)} — Anti-patterns

These are mistakes the skill should NOT make. Each entry is a specific failure mode observed (or anticipated) with a description of what goes wrong and how to avoid it.

## ❌ [Anti-pattern title]

**What happens:** [the failure mode in concrete terms]

**Why it's wrong:** [the reason this fails]

**How to avoid:** [the rule that prevents it]

---

(Add more entries as you observe failures. This file is the single most valuable artifact in the skill — it teaches Claude what NOT to do.)
`;

const TEMPLATE_GOOD_README = (name) => `# Good output examples

After your first successful run of \`/${name}\`, save the output here as a golden example.

Real positive samples beat synthetic ones — Claude pattern-matches against concrete examples better than abstract instructions.
`;

function titleCase(s) {
  return s.split('-').map(w => w[0]?.toUpperCase() + w.slice(1)).join(' ');
}

export async function dispatchSkill(args) {
  if (args.length === 0 || args[0] === '--help') {
    process.stdout.write(HELP);
    return;
  }
  const sub = args[0];
  const rest = args.slice(1);
  switch (sub) {
    case 'new':
      await scaffold(rest);
      break;
    case 'check':
      await check(rest);
      break;
    case 'list':
      await listAll(rest);
      break;
    default:
      fail(`unknown skill subcommand: ${sub}`);
  }
}

async function scaffold(args) {
  const name = args[0];
  if (!name || name.startsWith('--')) fail('vault skill new requires a skill name');
  if (!/^[a-z0-9-]+$/.test(name)) fail('skill name must be kebab-case (lowercase, digits, hyphens)');

  const skillDir = resolve(SKILLS_DIR, name);
  if (existsSync(skillDir)) fail(`skill already exists: ${skillDir}`);

  const descIdx = args.indexOf('--description');
  const description = descIdx !== -1 ? args[descIdx + 1] : `[Describe what ${name} does and when to fire.]`;
  const modelIdx = args.indexOf('--model');
  const model = modelIdx !== -1 ? args[modelIdx + 1] : null;

  mkdirSync(skillDir);
  mkdirSync(resolve(skillDir, 'examples'));
  mkdirSync(resolve(skillDir, 'examples/good'));
  mkdirSync(resolve(skillDir, 'examples/bad'));
  mkdirSync(resolve(skillDir, 'prompts'));
  mkdirSync(resolve(skillDir, 'reference'));
  mkdirSync(resolve(skillDir, 'templates'));

  writeFileSync(resolve(skillDir, 'SKILL.md'), TEMPLATE_SKILL_MD(name, description, model));
  writeFileSync(resolve(skillDir, 'examples/bad/ANTIPATTERNS.md'), TEMPLATE_ANTIPATTERNS(name));
  writeFileSync(resolve(skillDir, 'examples/good/README.md'), TEMPLATE_GOOD_README(name));

  info(`scaffolded skill at ${skillDir}`);
  emit({
    ok: true,
    name,
    path: skillDir,
    files_created: [
      'SKILL.md',
      'examples/good/README.md',
      'examples/bad/ANTIPATTERNS.md',
      'prompts/ (empty)',
      'reference/ (empty)',
      'templates/ (empty)',
    ],
    next_steps: [
      `1. Edit ${skillDir}/SKILL.md — fill in description, triggers, workflow.`,
      `2. After first successful run, save the output to examples/good/.`,
      `3. As you observe failures, add entries to examples/bad/ANTIPATTERNS.md.`,
      `4. Run 'vault skill check ${name}' to validate.`,
    ],
  }, args);
}

async function check(args) {
  const name = args[0];
  if (!name) fail('vault skill check requires a skill name');

  const skillDir = resolve(SKILLS_DIR, name);
  if (!existsSync(skillDir)) fail(`skill not found: ${skillDir}`);

  const issues = [];
  const skillMd = resolve(skillDir, 'SKILL.md');

  if (!existsSync(skillMd)) {
    issues.push({ severity: 'critical', issue: 'SKILL.md missing' });
  } else {
    const content = readFileSync(skillMd, 'utf8');
    const lineCount = content.split('\n').length;
    if (lineCount > 500) {
      issues.push({ severity: 'high', issue: `SKILL.md is ${lineCount} lines (rule: under 500). Extract to examples/, prompts/, reference/, or templates/.` });
    }
    // Frontmatter check
    if (!content.startsWith('---\n')) {
      issues.push({ severity: 'critical', issue: 'SKILL.md missing frontmatter block' });
    } else {
      const fmEnd = content.indexOf('\n---\n', 4);
      if (fmEnd === -1) {
        issues.push({ severity: 'critical', issue: 'SKILL.md frontmatter block not closed' });
      } else {
        const fm = content.slice(4, fmEnd);
        if (!/^name:\s*\S/m.test(fm)) issues.push({ severity: 'critical', issue: 'frontmatter missing required: name' });
        if (!/^description:\s*\S/m.test(fm)) issues.push({ severity: 'critical', issue: 'frontmatter missing required: description' });
        if (!/^version:\s*\S/m.test(fm)) issues.push({ severity: 'medium', issue: 'frontmatter missing recommended: version' });
        const nameMatch = fm.match(/^name:\s*(\S+)/m);
        if (nameMatch && nameMatch[1] !== name) {
          issues.push({ severity: 'high', issue: `frontmatter name "${nameMatch[1]}" != folder name "${name}"` });
        }
      }
    }
    // Cross-references resolution check
    const refRe = /`([./~][^`]*\.(?:md|sh|py|js|ts))`/g;
    const refs = [...content.matchAll(refRe)].map(m => m[1]);
    for (const ref of refs) {
      const target = ref.startsWith('~/') ? ref.replace(/^~/, process.env.HOME) :
                     ref.startsWith('/') ? ref :
                     resolve(skillDir, ref);
      if (!existsSync(target) && !ref.includes('<') && !ref.includes('{')) {
        issues.push({ severity: 'medium', issue: `unresolved reference: ${ref}` });
      }
    }
  }

  // ANTIPATTERNS.md check
  const antipatternsMd = resolve(skillDir, 'examples/bad/ANTIPATTERNS.md');
  if (!existsSync(antipatternsMd)) {
    issues.push({ severity: 'high', issue: 'examples/bad/ANTIPATTERNS.md missing (anchored-examples-and-hard-gates rule)' });
  } else {
    const ap = readFileSync(antipatternsMd, 'utf8');
    if (ap.length < 200) {
      issues.push({ severity: 'medium', issue: `ANTIPATTERNS.md is only ${ap.length} chars — likely empty scaffold. Document at least one anti-pattern.` });
    }
  }

  const result = {
    name,
    path: skillDir,
    issues_count: issues.length,
    critical: issues.filter(i => i.severity === 'critical').length,
    high: issues.filter(i => i.severity === 'high').length,
    medium: issues.filter(i => i.severity === 'medium').length,
    issues,
  };
  emit(result, args);
  if (result.critical > 0 || result.high > 0) process.exit(1);
}

async function listAll(args) {
  if (!existsSync(SKILLS_DIR)) {
    emit({ count: 0, skills: [] }, args);
    return;
  }
  const entries = readdirSync(SKILLS_DIR);
  const skills = entries
    .filter(name => {
      if (name.startsWith('.') || name === '_shared') return false;
      const path = resolve(SKILLS_DIR, name);
      try {
        return statSync(path).isDirectory() && existsSync(resolve(path, 'SKILL.md'));
      } catch {
        return false;
      }
    })
    .map(name => {
      const skillMd = resolve(SKILLS_DIR, name, 'SKILL.md');
      try {
        const content = readFileSync(skillMd, 'utf8');
        const fmEnd = content.indexOf('\n---\n', 4);
        const fm = fmEnd !== -1 ? content.slice(4, fmEnd) : '';
        const versionM = fm.match(/^version:\s*(\S+)/m);
        return { name, version: versionM?.[1] ?? null };
      } catch {
        return { name, version: null };
      }
    });
  emit({ count: skills.length, skills }, args);
}
