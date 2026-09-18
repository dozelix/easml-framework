import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Wiki y documentación EASML. El contenido de src/content/docs/ es un
// artefacto generado por scripts/generar_indice.py (no se edita a mano).
// En Vercel: Root Directory = web/.
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
        {
          label: 'Módulos',
          items: [{ autogenerate: { directory: 'modulos' } }],
        },
      ],
    }),
  ],
});
