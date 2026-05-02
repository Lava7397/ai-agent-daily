import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

/**
 * Dev: basePath /shizi. Prod export: assetPrefix must be absolute /shizi/ so CSS/JS load when the page
 * is served at …/shizi without a trailing slash (relative ./bakery-assets breaks and resolves under /).
 */
const nextConfig: NextConfig = {
  output: "export",
  basePath: isProduction ? "" : "/shizi",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

if (isProduction) {
  (nextConfig as NextConfig).assetPrefix = "/shizi/";
}

export default nextConfig;
