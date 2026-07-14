"""Ventana de desafío interactivo para la GUI."""

import time
import tkinter as tk
from tkinter import ttk

from tui.laboratorio import LaboratorioInteractivo, DESAFIOS_POR_MODULO, CONFIG_DIFICULTADES
from gui.styles import *


class DesafioWindow(tk.Toplevel):
    """Ventana modal de desafío (quiz) con dificultad seleccionable."""

    def __init__(self, parent, modulo_key: str):
        super().__init__(parent)
        self.title(f"Desafío — {modulo_key}")
        self.geometry("700x600")
        self.minsize(600, 500)
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()

        self.modulo_key = modulo_key
        self.motor = LaboratorioInteractivo()
        self.desafios = DESAFIOS_POR_MODULO.get(modulo_key, [])
        self.indice = 0
        self.correctas = 0
        self.pistas = 0
        self.fallos = 0
        self.tiempo_inicio = 0.0
        self.respondiendo = False

        # Selector de dificultad
        self.var_dificultad = tk.StringVar(value="facil")
        self._construir_interfaz()
        self._mostrar_selector()

    def _construir_interfaz(self):
        self.marco = tk.Frame(self, bg=BG, padx=20, pady=20)
        self.marco.pack(fill=tk.BOTH, expand=True)

        self.titulo = tk.Label(self.marco, text=f"🎯 Desafío: {self.modulo_key}",
                               bg=BG, fg=ACCENT, font=FUENTE_LG)
        self.titulo.pack(pady=(0, 10))

        self.info = tk.Label(self.marco, text="", bg=BG, fg=TEXTO_DIM, font=FUENTE_SM)
        self.info.pack()

        self.area = tk.Frame(self.marco, bg=BG)
        self.area.pack(fill=tk.BOTH, expand=True, pady=10)

        self.botonera = tk.Frame(self.marco, bg=BG)
        self.botonera.pack(fill=tk.X, pady=5)

        self.resultado = tk.Label(self.marco, text="", bg=BG, fg=TEXTO, font=FUENTE,
                                  wraplength=600, justify="left")
        self.resultado.pack(fill=tk.X, pady=5)

        self.barra = ttk.Progressbar(self.marco, length=600, mode="determinate")
        self.barra.pack(pady=10)

    def _limpiar_area(self):
        for w in self.area.winfo_children():
            w.destroy()

    def _mostrar_selector(self):
        self._limpiar_area()
        self.resultado.configure(text="Selecciona la dificultad:")

        for clave, cfg in CONFIG_DIFICULTADES.items():
            rb = tk.Radiobutton(
                self.area, text=f"  {cfg['nombre']}  —  {cfg['descripcion']}",
                variable=self.var_dificultad, value=clave,
                bg=BG, fg=TEXTO, selectcolor=BG_PANEL,
                font=FUENTE, activebackground=BG_HOVER, activeforeground=ACCENT,
                cursor="hand2"
            )
            rb.pack(anchor="w", pady=4)

        btn = tk.Button(self.area, text="Comenzar", command=self._iniciar,
                        bg=ACCENT, fg=BG, font=FUENTE_BOLD, relief="flat",
                        padx=20, pady=6, cursor="hand2")
        btn.pack(pady=20)

    def _iniciar(self):
        self.motor.dificultad = self.var_dificultad.get()
        self.indice = 0
        self.correctas = 0
        self.pistas = 0
        self.fallos = 0
        self.tiempo_inicio = time.time()
        self._mostrar_pregunta()

    def _mostrar_pregunta(self):
        if self.indice >= len(self.desafios):
            self._finalizar()
            return

        self._limpiar_area()
        d = self.desafios[self.indice]
        cfg = self.motor.obtener_config()
        self.info.configure(text=f"Dificultad: {cfg['nombre']}  |  Pregunta {self.indice+1}/{len(self.desafios)}")

        lbl = tk.Label(self.area, text=d.pregunta, bg=BG, fg=TEXTO, font=FUENTE_BOLD,
                       wraplength=600, justify="left")
        lbl.pack(anchor="w", pady=(0, 10))

        for i, opcion in enumerate(d.opciones):
            btn = tk.Button(self.area, text=f"  {i+1}. {opcion}",
                            command=lambda idx=i: self._responder(idx),
                            bg="#1a1d27", fg=TEXTO, font=FUENTE,
                            activebackground=BG_HOVER, activeforeground=ACCENT,
                            relief="flat", anchor="w", padx=10, pady=4,
                            cursor="hand2")
            btn.pack(fill=tk.X, pady=2)

        if self.pistas >= cfg["max_pistas"]:
            pista_btn = tk.Button(self.area, text="💡 Pista agotada",
                                  bg=BG_PANEL, fg=TEXTO_DIM, font=FUENTE_SM,
                                  relief="flat", state="disabled")
            pista_btn.pack(anchor="w", pady=8)
        else:
            pista_btn = tk.Button(self.area, text=f"💡 Pedir pista ({cfg['max_pistas'] - self.pistas} restantes)",
                                  command=self._pedir_pista,
                                  bg="#1a1d27", fg=AMARILLO, font=FUENTE_SM,
                                  activebackground=BG_HOVER, cursor="hand2",
                                  relief="flat")
            pista_btn.pack(anchor="w", pady=8)

        self.barra["maximum"] = len(self.desafios)
        self.barra["value"] = self.indice
        self.respondiendo = True

    def _responder(self, idx: int):
        if not self.respondiendo:
            return
        d = self.desafios[self.indice]
        correcto, mensaje = self.motor.evaluar_respuesta(d, idx, self.pistas)

        if correcto:
            self.correctas += 1
            self.resultado.configure(text=f"✅ Correcto!  {d.explicacion}", fg=VERDE)
        else:
            self.fallos += 1
            self.resultado.configure(text=f"❌ {mensaje}", fg=ROJO)

        self.respondiendo = False
        self.after(2000, self._avanzar)

    def _pedir_pista(self):
        cfg = self.motor.obtener_config()
        if self.pistas >= cfg["max_pistas"]:
            return
        d = self.desafios[self.indice]
        self.pistas += 1
        self.resultado.configure(text=f"💡 {d.pista}", fg=AMARILLO)

    def _avanzar(self):
        self.indice += 1
        self.pistas = 0
        self.resultado.configure(text="")
        self._mostrar_pregunta()

    def _finalizar(self):
        self._limpiar_area()
        tiempo = time.time() - self.tiempo_inicio
        puntos = self.motor.calcular_puntuacion(self.pistas, self.fallos,
                                                len(self.desafios), self.correctas)
        aprobado = self.correctas >= len(self.desafios) * 0.6
        estado = "✅ APROBADO" if aprobado else "❌ NO APROBADO"

        self.motor.guardar_resultado(self.modulo_key, self.pistas, self.fallos,
                                     tiempo, puntos, aprobado)

        resumen = (
            f"🏆 Resultado\n\n"
            f"  Correctas: {self.correctas}/{len(self.desafios)}\n"
            f"  Puntos:    {puntos}\n"
            f"  Tiempo:    {tiempo:.1f}s\n"
            f"  Estado:    {estado}\n\n"
            f"{self.motor.resumen_general()}"
        )

        lbl = tk.Label(self.area, text=resumen, bg=BG, fg=TEXTO,
                       font=FUENTE, justify="left")
        lbl.pack(anchor="w")

        cerrar = tk.Button(self.area, text="Cerrar", command=self.destroy,
                           bg=ACCENT, fg=BG, font=FUENTE_BOLD,
                           relief="flat", padx=20, pady=6, cursor="hand2")
        cerrar.pack(pady=20)

        self.barra["value"] = len(self.desafios)
