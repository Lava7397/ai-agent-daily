import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { cpSync, existsSync, mkdirSync, rmSync } from "fs";

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

console.log("Synced static export →", dest);
