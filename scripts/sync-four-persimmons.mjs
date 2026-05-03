/**
 * Copies Next static export into repo root ./shizi/
 * Renames _next → bakery-assets (avoid _next path quirks).
 * Public URL: /shizi/ (formerly /four-persimmons/).
 */
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from "fs";
import { dirname, extname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const siteOut = join(root, "sites", "four-persimmons", "out");
/** Primary deploy folder for the bakery mini-site */
const dest = join(root, "shizi");

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

/** Folders copied from Next `out/` (e.g. `public/bakery/` → `out/bakery/`) */
const OUT_EXTRAS = ["bakery"];
for (const name of OUT_EXTRAS) {
  const p = join(siteOut, name);
  if (existsSync(p)) {
    cpSync(p, join(dest, name), { recursive: true });
    console.log("Synced", name, "→", join(dest, name));
  }
}

/** @param {string} file */
function rewriteAssetPaths(file) {
  let s = readFileSync(file, "utf8");
  let n = s;
  n = n.replaceAll("_next/static", "bakery-assets/static");
  n = n.replaceAll("_next\\/static", "bakery-assets\\/static");
  n = n.replaceAll("/_next/static", "/bakery-assets/static");
  n = n.replaceAll("./_next/", "./bakery-assets/");
  n = n.replaceAll("./bakery-assets/", "/shizi/bakery-assets/");
  n = n.replaceAll("./bakery-assets\\/", "/shizi/bakery-assets\\/");
  if (n !== s) writeFileSync(file, n);
}

const TEXT_EXT = new Set([".html", ".js", ".css", ".json", ".txt", ".map"]);

/** @param {string} dir */
function walk(dir) {
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) walk(p);
    else {
      const ext = extname(ent.name).toLowerCase();
      if (TEXT_EXT.has(ext)) rewriteAssetPaths(p);
    }
  }
}

walk(dest);

console.log("Synced bakery static export →", dest);
