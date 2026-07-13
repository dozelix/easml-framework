"""Orquestador asíncrono para la ejecución de scripts del laboratorio."""

import os
import sys
import asyncio
from tui.utils import strip_ansi, format_log_line

async def run_lab_script(script_path: str, root_dir: str, log_widget) -> int:
    """Ejecuta un script de Python de forma asíncrona y envía la salida formateada al widget log."""
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=root_dir,
        )
        assert process.stdout is not None
        
        while True:
            raw_line = await process.stdout.readline()
            if not raw_line:
                break
            
            line = raw_line.decode("utf-8", errors="replace").rstrip("\n")
            clean = strip_ansi(line)
            
            if clean.strip():
                formatted = format_log_line(line, clean)
                log_widget.write(formatted)
                
        await process.wait()
        return process.returncode
    except Exception as e:
        log_widget.write(f"[bold red]ERROR DE PROCESO:[/] {e}")
        return -1