#!/usr/bin/env python3
"""Convierte todos los README.md a guia.html con estilo neobrutalista."""

import os
import markdown

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULOS_DIR = os.path.join(RAIZ, 'modulos')

CSS = """\
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #FFF8F0;
  color: #1A1A1A;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 10pt;
  line-height: 1.6;
  padding: 24px;
  max-width: 720px;
  margin: 0 auto;
}
h1 { font-size: 16pt; font-weight: bold; color: #2563EB; margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 2px solid #1A1A1A; }
h2 { font-size: 13pt; font-weight: bold; color: #2563EB; margin: 14px 0 6px; }
h3 { font-size: 11pt; font-weight: bold; color: #2563EB; margin: 12px 0 4px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0; padding-left: 24px; }
li { margin: 2px 0; }
code {
  background: #F0EBE3;
  color: #D6394A;
  padding: 1px 5px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9pt;
}
pre {
  background: #1A1A1A;
  color: #9ECE6A;
  padding: 12px;
  border: 2px solid #1A1A1A;
  margin: 8px 0;
  overflow-x: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9pt;
}
pre code { background: none; color: inherit; padding: 0; }
a { color: #2563EB; text-decoration: underline; }
a:hover { color: #7C3AED; }
table { border-collapse: collapse; margin: 8px 0; width: 100%; }
th, td { border: 1px solid #1A1A1A; padding: 6px 10px; text-align: left; }
th { background: #F0EBE3; font-weight: bold; }
</style>
"""

def convertir(md_path: str, html_path: str):
    with open(md_path, 'r', encoding='utf-8') as f:
        md = f.read()

    body = markdown.markdown(md, extensions=['fenced_code', 'codehilite', 'tables'])
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guía del Módulo</title>
{CSS}
</head>
<body>
{body}
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✓ {os.path.basename(html_path)}")


def main():
    for nombre in sorted(os.listdir(MODULOS_DIR)):
        dir_mod = os.path.join(MODULOS_DIR, nombre)
        if not os.path.isdir(dir_mod) or nombre == 'common':
            continue
        md_path = os.path.join(dir_mod, 'README.md')
        if not os.path.exists(md_path):
            print(f"  - {nombre}: sin README.md")
            continue
        html_path = os.path.join(dir_mod, 'guia.html')
        convertir(md_path, html_path)
    print("\nListo. %d módulos convertidos." % len([d for d in os.listdir(MODULOS_DIR) if os.path.isdir(os.path.join(MODULOS_DIR, d)) and d != 'common' and os.path.exists(os.path.join(MODULOS_DIR, d, 'README.md'))]))


if __name__ == '__main__':
    main()
