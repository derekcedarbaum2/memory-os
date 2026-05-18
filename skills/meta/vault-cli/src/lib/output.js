// Output helpers. Conventions:
// - JSON output on --json flag OR when stdout is non-TTY (gh CLI convention).
// - Human output is short, grep-friendly. No tables for non-TTY.

import { IS_TTY } from './config.js';

export function shouldEmitJson(args) {
  return args.includes('--json') || !IS_TTY;
}

export function emit(data, args) {
  if (shouldEmitJson(args)) {
    process.stdout.write(JSON.stringify(data, null, 2) + '\n');
  } else {
    if (typeof data === 'string') {
      process.stdout.write(data + '\n');
    } else {
      process.stdout.write(JSON.stringify(data, null, 2) + '\n');
    }
  }
}

export function info(msg) {
  process.stderr.write(`[vault] ${msg}\n`);
}

export function warn(msg) {
  process.stderr.write(`[vault] WARN: ${msg}\n`);
}

export function fail(msg, code = 1) {
  process.stderr.write(`[vault] ERROR: ${msg}\n`);
  process.exit(code);
}
