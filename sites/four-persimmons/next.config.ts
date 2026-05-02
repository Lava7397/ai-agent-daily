import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/four-persimmons",
  assetPrefix: "/four-persimmons/",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
