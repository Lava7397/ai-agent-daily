/**
 * Copies Next static export into repo root ./four-persimmons/.
 * Renames _next → bakery-assets: some hosts treat paths under "_" oddly; URLs stay predictable.
 */
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, statSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const siteOut = join(root, "sites", "four-persimmons", "out");
const dest = join(root, "four-persimmons");

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });

const nextStatics = join(siteOut, "_next");
const indexHtml = join(siteOut, "index.html");
if (!existsSync(nextStatics) || !existsSync(indexHtml)) {
  console.error("Missing Next export:", siteOut);
  process.exit(1);
}

cpSync(nextStatics, join(dest, "_next"), { recursive: true });
cpSync(indexHtml, join(dest, "index.html"));

const notFoundHtml = join(siteOut, "404.html");
if (existsSync(notFoundHtml)) cpSync(notFoundHtml, join(dest, "404.html"));
const nfDir = join(siteOut, "404");
if (existsSync(nfDir)) cpSync(nfDir, join(dest, "404"), { recursive: true });

const fromAssets = join(dest, "_next");
const toAssets = join(dest, "bakery-assets");
if (!existsSync(fromAssets)) {
  console.error("Expected _next in export");
  process.exit(1);
}
renameSync(fromAssets, toAssets);

/** @param {string} file */
function rewriteAssetPaths(file) {
  let s = readFileSync(file, "utf8");
  let n = s;
  // Only alter Next asset path segments (avoid touching unrelated "__NEXT*" strings).
  n = n.replaceAll("_next/static", "bakery-assets/static");
  n = n.replaceAll("_next\\/static", "bakery-assets\\/static");
  n = n.replaceAll("/_next/static", "/bakery-assets/static");
  n = n.replaceAll("./_next/", "./bakery-assets/");
  if (n !== s) writeFileSync(file, n);
}

/** @param {string} dir */
function walk(dir) {
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) walk(p);
    else rewriteAssetPaths(p);
  }
}

walk(dest);

console.log("Synced static export →", dest);
