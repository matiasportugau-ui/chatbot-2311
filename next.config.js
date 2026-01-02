/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove 'standalone' for Vercel deployment
  images: {
    domains: ['localhost'],
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  // Optimize for Vercel
  experimental: {
    outputFileTracingExcludes: {
      '*': [
        'node_modules/@swc/core-linux-x64-gnu',
        'node_modules/@swc/core-linux-x64-musl',
        'node_modules/@esbuild/linux-x64',
        '.git/**/*',
        'backups/**/*',
        'python-scripts/**/*',
      ],
    },
  },
}

module.exports = nextConfig
