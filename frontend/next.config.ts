import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Permitir que esta IP específica acceda a los recursos de desarrollo
  allowedDevOrigins: ["192.168.182.1", "localhost"],
};

export default nextConfig;
