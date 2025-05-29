/** @type {import('next').NextConfig} */

const nextConfig = {
  output: 'standalone', // Enables Next.js outputting a standalone folder
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
