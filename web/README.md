# easml-docs (web/)

Wiki y documentación del laboratorio, desplegada en Vercel (Root Directory: `web/`).

```bash
pnpm install     # instalar (una vez)
pnpm dev         # desarrollo (regenera docs antes de servir)
pnpm build       # build prod (regenera docs + Astro)
```

El contenido (`src/content/docs/`, `src/data/modulos.json`) **no se edita a mano**:
se genera desde `modulos/*/README.md` + `app/config.py` con:

```bash
python3 ../scripts/generar_indice.py          # generar
python3 ../scripts/generar_indice.py --check  # validar (lo corre el CI)
```
