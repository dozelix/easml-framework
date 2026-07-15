import time
import tkinter as tk
from tkinter import ttk

from app.laboratorio import LaboratorioInteractivo, DESAFIOS_POR_MODULO, CONFIG_DIFICULTADES
from gui.styles import *


class DesafioWindow(tk.Toplevel):
    def __init__(self, parent, modulo_key: str):
        super().__init__(parent)
        self.title(f"Desafio — {modulo_key}")
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

        self.var_dificultad = tk.StringVar(value="facil")
        self._construir_interfaz()
        self._mostrar_selector()

    def _construir_interfaz(self):
        self.marco = tk.Frame(self, bg=BG, padx=20, pady=20)
        self.marco.pack(fill=tk.BOTH, expand=True)

        self.titulo = tk.Label(self.marco, text=f"DESAFIO: {self.modulo_key}",
                               bg=BG, fg=ACCENT, font=FUENTE_H2)
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
            card = tk.Frame(self.area, bg=BG_CARD, highlightbackground=BORDE_CARD,
                            highlightthickness=2, padx=12, pady=8)
            card.pack(fill=tk.X, pady=3)
            rb = tk.Radiobutton(
                card, text=f"  {cfg['nombre']}  —  {cfg['descripcion']}",
                variable=self.var_dificultad, value=clave,
                bg=BG_CARD, fg=TEXTO, selectcolor=BG_PANEL,
                font=FUENTE, activebackground=BG_HOVER, activeforeground=ACCENT,
                cursor="hand2"
            )
            rb.pack(anchor="w")

        btn = tk.Button(self.area, text="Comenzar", command=self._iniciar,
                        bg=ACCENT, fg="#FFFFFF", font=FUENTE_BOLD, relief="solid",
                        padx=20, pady=6, cursor="hand2",
                        highlightbackground=BORDE_CARD, highlightthickness=1)
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

        card_preg = tk.Frame(self.area, bg=BG_CARD, highlightbackground=BORDE_CARD,
                             highlightthickness=2, padx=14, pady=12)
        card_preg.pack(fill=tk.X, pady=(0, 10))
        tk.Label(card_preg, text=d.pregunta, bg=BG_CARD, fg=TEXTO,
                 font=FUENTE_BOLD, wraplength=580, justify="left").pack(anchor="w")

        for i, opcion in enumerate(d.opciones):
            card_opt = tk.Frame(self.area, bg=BG_CARD, highlightbackground=BORDE_CARD,
                                highlightthickness=2, padx=12, pady=6)
            card_opt.pack(fill=tk.X, pady=2)
            btn = tk.Button(card_opt, text=f"  {i+1}. {opcion}",
                            command=lambda idx=i: self._responder(idx),
                            bg=BG_CARD, fg=TEXTO, font=FUENTE,
                            activebackground=BG_HOVER, activeforeground=ACCENT,
                            relief="flat", anchor="w", cursor="hand2")
            btn.pack(fill=tk.X)

        card_pista = tk.Frame(self.area, bg=BG_CARD, highlightbackground=BORDE_CARD,
                              highlightthickness=2, padx=12, pady=6)
        card_pista.pack(fill=tk.X, pady=(8, 0))
        if self.pistas >= cfg["max_pistas"]:
            tk.Label(card_pista, text="[PISTA] Agotada",
                     bg=BG_CARD, fg=TEXTO_DIM, font=FUENTE_SM).pack(anchor="w")
        else:
            btn_pista = tk.Button(card_pista,
                                  text=f"[PISTA] Pedir pista ({cfg['max_pistas'] - self.pistas} restantes)",
                                  command=self._pedir_pista,
                                  bg=BG_CARD, fg=AMARILLO, font=FUENTE_SM,
                                  activebackground=BG_HOVER, cursor="hand2",
                                  relief="flat")
            btn_pista.pack(anchor="w")

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
            self.resultado.configure(text=f"[OK] Correcto!  {d.explicacion}", fg=VERDE)
        else:
            self.fallos += 1
            self.resultado.configure(text=f"[--] {mensaje}", fg=ROJO)

        self.respondiendo = False
        self.after(2000, self._avanzar)

    def _pedir_pista(self):
        cfg = self.motor.obtener_config()
        if self.pistas >= cfg["max_pistas"]:
            return
        d = self.desafios[self.indice]
        self.pistas += 1
        self.resultado.configure(text=f"[PISTA] {d.pista}", fg=AMARILLO)

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
        estado = "[OK] APROBADO" if aprobado else "[--] NO APROBADO"

        self.motor.guardar_resultado(self.modulo_key, self.pistas, self.fallos,
                                     tiempo, puntos, aprobado)

        card_res = tk.Frame(self.area, bg=BG_CARD, highlightbackground=BORDE_CARD,
                            highlightthickness=2, padx=18, pady=14)
        card_res.pack(fill=tk.X, pady=(0, 16))

        tk.Label(card_res, text="RESULTADO", bg=BG_CARD, fg=ACCENT,
                 font=FUENTE_H2).pack(anchor="w", pady=(0, 8))

        for lbl, val in [
            ("Correctas", f"{self.correctas}/{len(self.desafios)}"),
            ("Puntos", str(puntos)),
            ("Tiempo", f"{tiempo:.1f}s"),
            ("Estado", estado),
        ]:
            row = tk.Frame(card_res, bg=BG_CARD)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=lbl, bg=BG_CARD, fg=TEXTO_DIM,
                     font=FUENTE, width=12, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=val, bg=BG_CARD, fg=TEXTO,
                     font=FUENTE_BOLD).pack(side=tk.LEFT)

        resumen = self.motor.resumen_general()
        if "RESUMEN" in resumen:
            tk.Label(card_res, text="", bg=BG_CARD).pack()
            tk.Label(card_res, text=resumen, bg=BG_CARD, fg=TEXTO_DIM,
                     font=FUENTE_SM, justify="left").pack(anchor="w")

        cerrar = tk.Button(self.area, text="Cerrar", command=self.destroy,
                           bg=ACCENT, fg="#FFFFFF", font=FUENTE_BOLD,
                           relief="solid", padx=20, pady=6, cursor="hand2",
                           highlightbackground=BORDE_CARD, highlightthickness=1)
        cerrar.pack(pady=10)

        self.barra["value"] = len(self.desafios)
