/** @type {import('next').NextConfig} */
const nextConfig = {
  // Core features
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false, // Security: remove X-Powered-By header
  
  // Skip type checking and linting during build
  // (we handle this in CI separately)
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Images (your app will use images for products)
  images: {
    domains: [], // Add your CDN domains here when needed
    formats: ['image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
  
  // Compiler optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Production optimizations
  compress: true,
  generateEtags: true,
  
  // Optimized for deployment
  output: 'standalone',
};

module.exports = nextConfig;