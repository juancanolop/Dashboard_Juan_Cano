/** @type {import('next').NextConfig} */
const nextConfig = {
  // react-leaflet v4's MapContainer isn't safe under React 18 Strict Mode's
  // dev-only double-invoked effects (it throws "Map container is already
  // initialized"). Strict Mode's extra checks only run in `next dev` anyway,
  // so turning it off doesn't change production (`next build`) behavior.
  reactStrictMode: false,
  // Don't auto-generate AGENTS.md/CLAUDE.md on every `next dev` run.
  agentRules: false,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "res.cloudinary.com",
      },
    ],
  },
};

export default nextConfig;
