import path from "node:path";

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    cpus: 1,
  },
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
