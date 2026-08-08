/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.VERCEL ? undefined : 'standalone',

  async rewrites() {
    // BACKEND_URL is a server-side-only env var set in Vercel dashboard.
    // Falls back to NEXT_PUBLIC_API_URL then localhost for local dev.
    const backendUrl =
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      'https://pramaan-shield-backend.onrender.com';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`
      },
      {
        source: '/health',
        destination: `${backendUrl}/health`
      }
    ];
  },

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob:",
              "connect-src 'self' http://localhost:8000 https://pramaan-shield-backend.onrender.com https://*.onrender.com https://*.hf.space https://*.vercel.app",
            ].join('; ')
          }
        ]
      }
    ];
  }
};

module.exports = nextConfig;
