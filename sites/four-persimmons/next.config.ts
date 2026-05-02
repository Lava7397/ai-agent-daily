import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

/** Dev: serve under /four-persimmons for parity with deployed URL. Prod export: flat output + relative ./assets for static host subfolders. */
const nextConfig: NextConfig = {
  output: "export",
  basePath: isProduction ? "" : "/four-persimmons",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

if (isProduction) {
  (nextConfig as NextConfig).assetPrefix = "./";
}

export default nextConfig;
