import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Wiki y documentación EASML. El contenido de src/content/docs/ es un
// artefacto generado por scripts/generar_indice.py (no se edita a mano).
// En Vercel: Root Directory = web/.
// Mermaid: Starlight no lo renderiza nativo (mostraba código). Se renderiza
// en cliente con mermaid@11 fijado (head). El build-time se descartó:
// rehype-mermaid exige playwright (navegador real) solo por importarlo.
const mermaidInit = `
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
for (const bloque of document.querySelectorAll('pre[data-language="mermaid"] > code')) {
  const lineas = [...bloque.querySelectorAll('.ec-line')];
  const fuente = lineas.length
    ? lineas.map((l) => l.textContent).join('\\n')
    : bloque.textContent;
  const pre = document.createElement('pre');
  pre.className = 'mermaid not-content';
  pre.textContent = fuente;
  const marco = bloque.closest('figure') ?? bloque.parentElement;
  marco.replaceWith(pre);
}
mermaid.initialize({
  startOnLoad: false,
  theme: document.documentElement.dataset.theme === 'dark' ? 'dark' : 'default',
});
await mermaid.run();
`;

export default defineConfig({
  integrations: [
    starlight({
      title: 'EASML',
      description: 'Wiki y documentación del laboratorio educativo de malware',
      defaultLocale: 'root',
      locales: {
        root: { label: 'Español', lang: 'es' },
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/dozelix/easml-framework',
        },
      ],
      sidebar: [
        { label: 'Descargas', slug: 'descargas' },
        {
          label: 'Módulos',
          items: [{ autogenerate: { directory: 'modulos' } }],
        },
      ],
      head: [
        {
          tag: 'script',
          attrs: { type: 'module' },
          content: mermaidInit,
        },
      ],
    }),
  ],
});
