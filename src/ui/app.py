"""Ventana principal del analizador léxico."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from ..analysis_service import NFAAnalysis, analyze_nfa, analyze_optional_dfas
from . import theme
from .components import ScrollableFrame, card, clear_children, info_row


class LexerApp:
    """Interfaz de una sola vista para analizar expresiones regulares."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Analizador Léxico")
        self.root.minsize(860, 650)
        self.root.configure(background=theme.BACKGROUND)
        theme.apply_theme(root)

        self.expression_var = tk.StringVar(value="(a|b)*abb(a|b)*")
        self.word_var = tk.StringVar(value="babbaaaaa")
        self.file_var = tk.StringVar(value="También puedes cargar un archivo .txt")
        self._loaded_expressions: list[str] = []

        self._build_layout()
        self._show_empty_result()
        self.root.bind("<Return>", lambda _event: self.analyze())

    def _build_layout(self) -> None:
        scrollable = ScrollableFrame(self.root)
        scrollable.pack(fill="both", expand=True)
        content = scrollable.content
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        hero = ttk.Frame(content, style="App.TFrame", padding=(34, 30, 34, 18))
        hero.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(hero, text="Analizador Léxico", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            hero,
            text="Expresión regular → AFN → AFD → AFD mínimo",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        self._build_input_card(content)

        self.status_card = card(content, "Resultado", "La respuesta aparece después de analizar la cadena")
        self.status_card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 12))
        self.status_content = self.status_card.winfo_children()[-1]

        self.summary_card = card(content, "Transformación", "Detalles de la expresión que ingresaste")
        self.summary_card.grid(row=3, column=0, sticky="nsew", padx=(34, 6), pady=(0, 12))
        self.summary_content = self.summary_card.winfo_children()[-1]

        self.trace_card = card(content, "Recorrido del AFN", "Estados activos durante la simulación")
        self.trace_card.grid(row=3, column=1, sticky="nsew", padx=(6, 34), pady=(0, 12))
        self.trace_content = self.trace_card.winfo_children()[-1]

        self.dfa_card = card(content, "AFD y AFD mínimo", "Resultados del módulo de determinización")
        self.dfa_card.grid(row=4, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 30))
        self.dfa_content = self.dfa_card.winfo_children()[-1]

    def _build_input_card(self, parent) -> None:
        input_card = card(parent, "Nueva evaluación", "Usa |, *, ( ) y concatenación implícita")
        input_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 12))
        content = input_card.winfo_children()[-1]
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Expresión regular", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(content, text="Cadena a evaluar", style="Muted.TLabel").grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Entry(content, textvariable=self.expression_var, style="App.TEntry").grid(row=1, column=0, sticky="ew", pady=(5, 14))
        ttk.Entry(content, textvariable=self.word_var, style="App.TEntry").grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(5, 14))

        actions = ttk.Frame(content, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=2, sticky="ew")
        actions.columnconfigure(2, weight=1)
        ttk.Button(actions, text="Analizar cadena", style="Accent.TButton", command=self.analyze).grid(row=0, column=0, sticky="w")
        ttk.Button(actions, text="Cargar archivo .txt", style="Secondary.TButton", command=self.load_file).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(actions, textvariable=self.file_var, style="Muted.TLabel").grid(row=0, column=2, sticky="e", padx=(12, 0))

        self.expression_picker = ttk.Combobox(content, style="App.TCombobox", state="readonly")
        self.expression_picker.bind("<<ComboboxSelected>>", self._select_loaded_expression)

    def _show_empty_result(self) -> None:
        clear_children(self.status_content)
        ttk.Label(self.status_content, text="Listo para empezar", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.status_content,
            text="Ingresa una expresión y una cadena; el resultado aparecerá aquí.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._show_placeholder_details()

    def _show_placeholder_details(self) -> None:
        clear_children(self.summary_content)
        clear_children(self.trace_content)
        clear_children(self.dfa_content)
        ttk.Label(self.summary_content, text="Aún no hay una expresión analizada.", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.trace_content, text="Aquí se mostrarán los estados activos del AFN.", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.dfa_content,
            text="Las tarjetas del AFD aparecerán al integrar el módulo de tu compañero.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w")

    def _show_error(self, message: str) -> None:
        clear_children(self.status_content)
        ttk.Label(self.status_content, text="Revisa la expresión", style="CardTitle.TLabel", foreground=theme.RED).grid(row=0, column=0, sticky="w")
        ttk.Label(self.status_content, text=message, style="Muted.TLabel", wraplength=720).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._show_placeholder_details()

    def analyze(self) -> None:
        """Ejecuta la parte AFN y actualiza la vista sin cerrar la aplicación."""
        expression = self.expression_var.get().strip()
        word = self.word_var.get()
        try:
            analysis = analyze_nfa(expression, word)
        except ValueError as error:
            self._show_error(str(error))
            return

        self._show_nfa_analysis(analysis)

    def _show_nfa_analysis(self, analysis: NFAAnalysis) -> None:
        clear_children(self.status_content)
        accepted = analysis.accepts_word
        title = "Cadena aceptada" if accepted else "Cadena no aceptada"
        explanation = (
            "La cadena pertenece al lenguaje de la expresión regular."
            if accepted
            else "La cadena no pertenece al lenguaje de la expresión regular."
        )
        color = theme.GREEN if accepted else theme.RED
        ttk.Label(self.status_content, text=title, style="CardTitle.TLabel", foreground=color).grid(row=0, column=0, sticky="w")
        ttk.Label(self.status_content, text=explanation, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        clear_children(self.summary_content)
        info_row(self.summary_content, 0, "Concatenación explícita", analysis.explicit_expression)
        info_row(self.summary_content, 1, "Postfix", analysis.postfix)
        info_row(self.summary_content, 2, "Estados del AFN", str(analysis.state_count))
        alphabet = ", ".join(analysis.alphabet) if analysis.alphabet else "∅"
        info_row(self.summary_content, 3, "Alfabeto", alphabet)

        clear_children(self.trace_content)
        for index, step in enumerate(analysis.trace):
            label = "Inicio (ε-cerradura)" if step.symbol is None else f"Después de '{step.symbol}'"
            states = "{" + ", ".join(map(str, sorted(step.states))) + "}"
            info_row(self.trace_content, index, label, states)

        self._show_dfa_results(analysis)

    def _show_dfa_results(self, analysis: NFAAnalysis) -> None:
        clear_children(self.dfa_content)
        try:
            dfa_results = analyze_optional_dfas(analysis.nfa, analysis.word)
        except Exception as error:  # El aporte externo no debe cerrar la interfaz.
            ttk.Label(self.dfa_content, text="El módulo AFD devolvió un error.", style="CardTitle.TLabel", foreground=theme.RED).grid(row=0, column=0, sticky="w")
            ttk.Label(self.dfa_content, text=str(error), style="Muted.TLabel", wraplength=720).grid(row=1, column=0, sticky="w", pady=(4, 0))
            return

        if not dfa_results:
            ttk.Label(
                self.dfa_content,
                text="El bloque AFN ya está listo. Esta sección se completará al integrar el AFD por subconjuntos y su minimización.",
                style="Muted.TLabel",
                wraplength=720,
            ).grid(row=0, column=0, sticky="w")
            return

        for row, result in enumerate(dfa_results):
            verdict = "acepta" if result.accepts_word else "no acepta"
            ttk.Label(self.dfa_content, text=result.title, style="CardTitle.TLabel").grid(row=row * 2, column=0, sticky="w", pady=(0 if row == 0 else 10, 0))
            ttk.Label(
                self.dfa_content,
                text=f"{result.state_count} estados · {verdict} la cadena",
                style="Muted.TLabel",
            ).grid(row=row * 2 + 1, column=0, sticky="w", pady=(2, 0))

    def load_file(self) -> None:
        """Carga expresiones no vacías desde un archivo, una por línea."""
        filename = filedialog.askopenfilename(
            title="Selecciona un archivo de expresiones",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return

        try:
            expressions = [line.strip() for line in Path(filename).read_text(encoding="utf-8").splitlines() if line.strip()]
        except OSError as error:
            self._show_error(f"No fue posible leer el archivo: {error}")
            return

        if not expressions:
            self._show_error("El archivo no contiene expresiones regulares.")
            return

        self._loaded_expressions = expressions
        self.expression_picker["values"] = expressions
        self.expression_picker.set(expressions[0])
        self.expression_var.set(expressions[0])
        self.file_var.set(f"{len(expressions)} expresión(es) cargada(s)")

        if not self.expression_picker.winfo_ismapped():
            self.expression_picker.master.grid_columnconfigure(0, weight=1)
            self.expression_picker.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def _select_loaded_expression(self, _event=None) -> None:
        selected = self.expression_picker.get()
        if selected:
            self.expression_var.set(selected)


def run() -> None:
    """Crea y muestra la ventana de la aplicación."""
    root = tk.Tk()
    LexerApp(root)
    root.mainloop()
