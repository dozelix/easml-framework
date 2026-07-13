"""Utilidades de formateo y manejo de texto para la TUI."""

import re

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(text: str) -> str:
    """Elimina secuencias de escape ANSI de una cadena."""
    return ANSI_RE.sub('', text)

def format_log_line(line: str, clean_text: str) -> str:
    """Aplica marcas de estilo Rich basándose en los tags de salida del laboratorio."""
    if any(tag in line for tag in ("[CIFRADO]", "[ELIMINADO]", "[CORROMPIDO]")):
        return f"[red]{clean_text}[/]"
    if any(tag in line for tag in ("[OK]", "[+] ", "eliminado:", "CREADO")):
        return f"[green]{clean_text}[/]"
    if any(tag in line for tag in ("[!]", "ADVERTENCIA", "ERROR")):
        return f"[yellow]{clean_text}[/]"
    if "FASE" in line or "===" in line:
        return f"[bold cyan]{clean_text}[/]"
    return clean_text