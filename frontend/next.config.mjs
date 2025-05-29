/** @type {import('next').NextConfig} */

const nextConfig = {
  output: 'standalone', // Enables Next.js outputting a standalone folder
  // Set assetPrefix for production to ensure static assets are loaded correctly
  // This should match the base URL where your frontend is served.
  assetPrefix: process.env.NEXT_PUBLIC_ASSET_PREFIX || undefined,
  basePath: '', // Set to empty string if served from the root of the domain

  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*', // Proxy to Backend
      },
      {
        source: '/auth/:path*',
        destination: 'http://backend:8000/auth/:path*', // Proxy to Backend for auth routes
      },
    ];
  },
};

export default nextConfig;
