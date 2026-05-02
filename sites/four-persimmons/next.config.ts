import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

/** Dev: serve under /shizi (matches production path). Prod export: relative ./bakery-assets under ./shizi/ */
const nextConfig: NextConfig = {
  output: "export",
  basePath: isProduction ? "" : "/shizi",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

if (isProduction) {
  (nextConfig as NextConfig).assetPrefix = "./";
}

export default nextConfig;
