/**
 * Download authorised shop images into sites/four-persimmons/public/bakery/
 *
 * Configure URLs in bakery-asset-urls.json (see bakery-asset-urls.example.json).
 * Only use direct image URLs you are allowed to host (e.g. merchant/OSS signed links).
 *
 * Usage: npm run fetch:bakery-assets
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const site = join(root, "sites", "four-persimmons");
const outDir = join(site, "public", "bakery");
const cfgPath = join(site, "bakery-asset-urls.json");

const ALLOWED_CT = /^image\/(jpeg|jpg|png|webp|gif|avif)|application\/octet-stream/i;

async function fetchOne(filename, url) {
  const u = String(url || "").trim();
  if (!u) return { filename, skipped: true };

  console.log(`GET ${filename} ← ${u.slice(0, 96)}${u.length > 96 ? "…" : ""}`);

  const res = await fetch(u, {
    redirect: "follow",
    headers: {
      Accept: "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
      "User-Agent":
        "Mozilla/5.0 (compatible; ShiziBrandAssets/1.0; +https://www.lava7397.com)",
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} for ${filename}`);
  }

  const ct = res.headers.get("content-type") || "";
  const buf = Buffer.from(await res.arrayBuffer());
  if (buf.length < 256) {
    throw new Error(`Body too small for ${filename}`);
  }

  const looksWebp = filename.toLowerCase().endsWith(".webp") && buf[8] === 87 && buf[9] === 69 && buf[10] === 66 && buf[11] === 80;
  const looksPng = filename.toLowerCase().endsWith(".png") && buf[0] === 0x89 && buf[1] === 0x50;
  const looksJpeg = /\.jpe?g$/i.test(filename) && buf[0] === 0xff && buf[1] === 0xd8;

  const ctOk =
    ALLOWED_CT.test(ct) ||
    /^image\//i.test(ct) ||
    looksWebp ||
    looksPng ||
    looksJpeg;

  if (!ctOk && !ALLOWED_CT.test(ct)) {
    console.warn(`  warn: unexpected Content-Type "${ct}" for ${filename} — saving anyway`);
  }

  writeFileSync(join(outDir, filename), buf);
  console.log(`  wrote ${filename} (${buf.length} bytes)`);
  return { filename, bytes: buf.length };
}

async function main() {
  if (!existsSync(cfgPath)) {
    console.error(
      `Missing ${cfgPath}\n` +
        `Copy bakery-asset-urls.example.json → bakery-asset-urls.json and paste direct image URLs from your authorised source (OSS / merchant console / etc.).`
    );
    process.exit(1);
  }

  let map;
  try {
    map = JSON.parse(readFileSync(cfgPath, "utf8"));
  } catch (e) {
    console.error("Invalid JSON in bakery-asset-urls.json:", e.message);
    process.exit(1);
  }

  mkdirSync(outDir, { recursive: true });

  const entries = Object.entries(map).filter(([k]) => typeof k === "string" && k.length > 0);
  if (entries.length === 0) {
    console.error("No entries in bakery-asset-urls.json");
    process.exit(1);
  }

  let done = 0;
  for (const [filename, url] of entries) {
    if (typeof url !== "string" || !url.trim()) continue;
    try {
      await fetchOne(filename, url);
      done += 1;
    } catch (e) {
      console.error(`Failed ${filename}:`, e.message);
      process.exitCode = 1;
    }
  }

  if (done === 0) {
    console.error("No non-empty URLs to fetch. Fill strings in bakery-asset-urls.json.");
    process.exit(1);
  }

  console.log(`Done. ${done} file(s) in ${outDir}`);
}

main();
