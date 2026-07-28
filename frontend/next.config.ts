import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a self-contained `.next/standalone` server for a minimal, non-root production
  // container image (see docker/frontend.Dockerfile).
  output: "standalone",
};

export default nextConfig;
