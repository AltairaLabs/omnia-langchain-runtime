/**
 * Mermaid diagram initialization script
 * Loads Mermaid from CDN and configures it for Starlight theme support
 */

const MERMAID_VERSION = '11.12.2';
const CDN_URL = `https://cdn.jsdelivr.net/npm/mermaid@${MERMAID_VERSION}/dist/mermaid.esm.min.mjs`;

// Theme configuration for dark/light modes
const getThemeConfig = (isDark) => ({
  theme: isDark ? 'dark' : 'default',
  themeVariables: {
    background: 'transparent',
    primaryColor: isDark ? '#8b5cf6' : '#7c3aed',
    primaryTextColor: isDark ? '#e5e7eb' : '#1f2937',
    primaryBorderColor: isDark ? '#6366f1' : '#4f46e5',
    lineColor: isDark ? '#6b7280' : '#9ca3af',
    secondaryColor: isDark ? '#374151' : '#e5e7eb',
    tertiaryColor: isDark ? '#1f2937' : '#f3f4f6',
  },
  fontFamily: 'system-ui, -apple-system, sans-serif',
});

// Initialize Mermaid diagrams
async function initMermaid() {
  const { default: mermaid } = await import(CDN_URL);

  const isDark = document.documentElement.dataset.theme === 'dark' ||
    (!document.documentElement.dataset.theme &&
     window.matchMedia('(prefers-color-scheme: dark)').matches);

  mermaid.initialize({
    startOnLoad: false,
    ...getThemeConfig(isDark),
  });

  // Find all mermaid code blocks
  const codeBlocks = document.querySelectorAll('pre > code.language-mermaid');

  for (const block of codeBlocks) {
    const pre = block.parentElement;
    const diagram = block.textContent;

    // Create container for rendered diagram
    const container = document.createElement('div');
    container.className = 'mermaid';

    try {
      const { svg } = await mermaid.render(
        `mermaid-${Math.random().toString(36).slice(2)}`,
        diagram
      );
      container.innerHTML = svg;
      pre.replaceWith(container);
    } catch (error) {
      console.error('Mermaid rendering error:', error);
    }
  }
}

// Re-render on theme change
function observeThemeChanges() {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.attributeName === 'data-theme') {
        // Re-initialize on theme change
        initMermaid();
        break;
      }
    }
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });
}

// Initialize on page load and Astro navigation
document.addEventListener('DOMContentLoaded', initMermaid);
document.addEventListener('astro:page-load', initMermaid);
observeThemeChanges();
