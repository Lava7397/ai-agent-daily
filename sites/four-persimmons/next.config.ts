import type { NextConfig } from "next";

/** Production-only relative asset URLs so `/four-persimmons/` works on static hosts without root-absolute `/four-persimmons/_next/` resolution issues. Dev keeps default absolute `/`. */
const nextConfig: NextConfig = {
  output: "export",
  basePath: "",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

if (process.env.NODE_ENV === "production") {
  (nextConfig as NextConfig).assetPrefix = "./";
}

export default nextConfig;
