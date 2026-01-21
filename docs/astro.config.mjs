// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightThemeGalaxy from 'starlight-theme-galaxy';
import d2 from 'astro-d2';

// Configure via environment variables for easy deployment changes
// For custom domain: SITE_URL=https://docs.example.com BASE_PATH=
// For GitHub Pages: SITE_URL=https://org.github.io BASE_PATH=/repo-name
const siteUrl = process.env.SITE_URL || 'https://altairalabs.github.io';
const basePath = process.env.BASE_PATH ?? '/omnia-langchain-runtime';

export default defineConfig({
  site: siteUrl,
  base: basePath,
  integrations: [
    d2(),
    starlight({
      title: 'Omnia LangChain Runtime',
      logo: {
        src: './public/logo.svg',
        alt: 'Omnia LangChain Runtime Logo',
      },
      plugins: [starlightThemeGalaxy()],
      customCss: ['./src/styles/custom.css'],
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/AltairaLabs/omnia-langchain-runtime' },
      ],
      sidebar: [
        { label: 'Getting Started', autogenerate: { directory: 'getting-started' } },
        { label: 'Providers', autogenerate: { directory: 'providers' } },
        { label: 'Session Management', autogenerate: { directory: 'session' } },
        { label: 'Tools', autogenerate: { directory: 'tools' } },
        { label: 'gRPC Protocol', autogenerate: { directory: 'grpc' } },
        { label: 'Deployment', autogenerate: { directory: 'deployment' } },
        { label: 'API Reference', autogenerate: { directory: 'api' } },
        { label: 'Contributors', autogenerate: { directory: 'contributors' } },
      ],
      head: [
        {
          tag: 'script',
          attrs: {
            type: 'module',
            src: `${basePath}/mermaid-init.js`,
          },
        },
      ],
    }),
  ],
});
