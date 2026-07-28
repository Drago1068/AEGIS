#!/usr/bin/env node
/**
 * Phase 0 must contain no scoring, recommendation, prediction, or trading logic.
 *
 * This is a structural check (file names and exported declaration names under `src/`), not
 * a naive whole-repository text grep, so documentation/comments cannot cause a false
 * failure. Test files are excluded from the scan. See
 * docs/architecture/decisions/0001-phase-0-tooling.md.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { basename, extname, join, relative } from "node:path";

const SRC_DIR = join(import.meta.dirname, "..", "src");

const FORBIDDEN_NAME_PATTERNS = [
  /^scor(e|ing)s?$/i,
  /^recommend(ation)?s?$/i,
  /^predict(ion)?s?$/i,
  /^trad(e|ing)s?$/i,
  /^orders?$/i,
];

const FORBIDDEN_EXPORT_PATTERNS = [
  /^score/i,
  /^recommend/i,
  /^predict/i,
  /^placeOrder/i,
  /^submitOrder/i,
  /^executeTrade/i,
];

const EXPORT_DECLARATION_RE =
  /export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let)\s+([A-Za-z_$][\w$]*)/g;

const SOURCE_EXTENSIONS = new Set([".ts", ".tsx"]);

function isTestFile(fileName) {
  return fileName.endsWith(".test.ts") || fileName.endsWith(".test.tsx");
}

function walk(dir) {
  const files = [];
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    const stats = statSync(fullPath);
    if (stats.isDirectory()) {
      files.push(...walk(fullPath));
    } else if (SOURCE_EXTENSIONS.has(extname(entry)) && !isTestFile(entry)) {
      files.push(fullPath);
    }
  }
  return files;
}

function main() {
  const files = walk(SRC_DIR);
  const violations = [];

  for (const file of files) {
    const stem = basename(file, extname(file));
    if (FORBIDDEN_NAME_PATTERNS.some((pattern) => pattern.test(stem))) {
      violations.push(`forbidden module name: ${relative(SRC_DIR, file)}`);
    }

    const content = readFileSync(file, "utf-8");
    for (const match of content.matchAll(EXPORT_DECLARATION_RE)) {
      const exportedName = match[1];
      if (FORBIDDEN_EXPORT_PATTERNS.some((pattern) => pattern.test(exportedName))) {
        violations.push(`forbidden export in ${relative(SRC_DIR, file)}: ${exportedName}`);
      }
    }
  }

  if (violations.length > 0) {
    console.error("No-domain-logic check failed:");
    for (const violation of violations) {
      console.error(`  - ${violation}`);
    }
    process.exitCode = 1;
    return;
  }

  console.log(`No-domain-logic check passed (${files.length} source files scanned).`);
}

main();
