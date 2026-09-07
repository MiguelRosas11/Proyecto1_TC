"""Ventana principal del analizador léxico."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..analysis_service import NFAAnalysis, analyze_nfa, analyze_optional_dfas
from ..batch_service import iter_file_analyses
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
        self.file_var = tk.StringVar()
        self.batch_context_var = tk.StringVar()
        self._batch_results = {}
        self._batch_job = None

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

        self._build_input_card(content)

        self.status_card = card(content, "Resultado")
        self.status_card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 12))
        self.status_content = self.status_card.winfo_children()[-1]

        self.summary_card = card(content, "Transformación")
        self.summary_card.grid(row=3, column=0, sticky="nsew", padx=(34, 6), pady=(0, 12))
        self.summary_content = self.summary_card.winfo_children()[-1]

        self.trace_card = card(content, "Recorrido del AFN")
        self.trace_card.grid(row=3, column=1, sticky="nsew", padx=(6, 34), pady=(0, 12))
        self.trace_content = self.trace_card.winfo_children()[-1]

        self.dfa_card = card(content, "Autómatas")
        self.dfa_card.grid(row=3, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 12))
        self.summary_card.grid_configure(row=4)
        self.trace_card.grid_configure(row=4)
        self.dfa_content = self.dfa_card.winfo_children()[-1]
        self.batch_card = card(content, "Archivo")
        self.batch_card.grid(row=5, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 30))
        batch_content = self.batch_card.winfo_children()[-1]
        ttk.Label(batch_content, textvariable=self.batch_context_var, style="Muted.TLabel", wraplength=720).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.batch_table = ttk.Treeview(batch_content, columns=("line", "regex", "nfa", "dfa", "min"), show="headings", height=6)
        for name, title, width in (("line", "Línea", 50), ("regex", "Expresión / error", 340), ("nfa", "AFN", 70), ("dfa", "AFD", 70), ("min", "Mínimo", 70)):
            self.batch_table.heading(name, text=title)
            self.batch_table.column(name, width=width, stretch=name == "regex")
        self.batch_table.grid(row=1, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(batch_content, orient="vertical", command=self.batch_table.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.batch_table.configure(yscrollcommand=scrollbar.set)
        self.batch_table.bind("<<TreeviewSelect>>", self._select_batch_result)
        ttk.Label(batch_content, textvariable=self.file_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.batch_card.grid_remove()

    def _build_input_card(self, parent) -> None:
        input_card = card(parent)
        input_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=34, pady=(0, 12))
        content = input_card.winfo_children()[-1]
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Expresión regular", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(content, text="Cadena", style="Muted.TLabel").grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Entry(content, textvariable=self.expression_var, style="App.TEntry").grid(row=1, column=0, sticky="ew", pady=(5, 14))
        ttk.Entry(content, textvariable=self.word_var, style="App.TEntry").grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(5, 14))

        actions = ttk.Frame(content, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=2, sticky="ew")
        actions.columnconfigure(2, weight=1)
        ttk.Button(actions, text="Analizar", style="Accent.TButton", command=self.analyze).grid(row=0, column=0, sticky="w")
        ttk.Button(actions, text="Cargar archivo .txt", style="Secondary.TButton", command=self.load_file).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(actions, text="Sintaxis", style="Secondary.TButton", command=self._show_syntax).grid(row=0, column=2, sticky="e")

    def _show_syntax(self) -> None:
        messagebox.showinfo(
            "Sintaxis",
            "a|b   Unión\na*   Cero o más repeticiones\nab o a.b   Concatenación\n( )   Agrupación\n"
            "ε   Palabra vacía en la expresión\n\n"
            "Para evaluar la cadena vacía, deja el campo Cadena vacío.\n"
            "Cada símbolo es un carácter. No se admiten espacios en la expresión.\n"
            "No se implementan atajos como +, ? o [a-z]; se leen como caracteres literales.",
            parent=self.root,
        )

    def _show_empty_result(self) -> None:
        self.status_card.grid_remove()
        self._hide_details()

    def _hide_details(self) -> None:
        for panel in (self.summary_card, self.trace_card, self.dfa_card):
            panel.grid_remove()

    def _show_error(self, message: str) -> None:
        clear_children(self.status_content)
        self.status_card.grid()
        ttk.Label(self.status_content, text=message, style="Body.TLabel", foreground=theme.RED, wraplength=720).grid(row=0, column=0, sticky="w")
        self._hide_details()

    def analyze(self) -> None:
        """Ejecuta los tres autómatas y actualiza la vista."""
        expression = self.expression_var.get().strip()
        word = self.word_var.get()
        try:
            analysis = analyze_nfa(expression, word)
            dfas = analyze_optional_dfas(analysis.nfa, word)
        except (ValueError, RuntimeError, OSError) as error:
            self._show_error(str(error))
            return

        self._show_nfa_analysis(analysis, dfas)

    def _show_nfa_analysis(self, analysis: NFAAnalysis, dfas) -> None:
        for panel in (self.status_card, self.summary_card, self.trace_card, self.dfa_card):
            panel.grid()
        clear_children(self.status_content)
        accepted = analysis.accepts_word
        title = "Cadena aceptada" if accepted else "Cadena no aceptada"
        color = theme.GREEN if accepted else theme.RED
        ttk.Label(self.status_content, text=title, style="CardTitle.TLabel", foreground=color).grid(row=0, column=0, sticky="w")

        clear_children(self.summary_content)
        info_row(self.summary_content, 0, "Concatenación explícita", analysis.explicit_expression)
        info_row(self.summary_content, 1, "Postfix", analysis.postfix)
        alphabet = ", ".join(analysis.alphabet) if analysis.alphabet else "∅"
        info_row(self.summary_content, 2, "Alfabeto", alphabet)
        info_row(self.summary_content, 3, "Cadena evaluada", analysis.word if analysis.word else "ε (vacía)")

        clear_children(self.trace_content)
        for index, step in enumerate(analysis.trace):
            label = "Inicio (ε-cerradura)" if step.symbol is None else f"Después de '{step.symbol}'"
            states = "{" + ", ".join(map(str, sorted(step.states))) + "}"
            info_row(self.trace_content, index, label, states)

        self._show_dfa_results(analysis, dfas)

    def _show_dfa_results(self, analysis: NFAAnalysis, dfa_results) -> None:
        clear_children(self.dfa_content)

        if not dfa_results:
            ttk.Label(
                self.dfa_content,
                text="No se encontraron resultados del AFD. Revisa la instalación.",
                style="Muted.TLabel",
                wraplength=720,
            ).grid(row=0, column=0, sticky="w")
            return

        for column, heading in enumerate(("Autómata", "Estados", "Acepta", "")):
            ttk.Label(self.dfa_content, text=heading, style="Muted.TLabel").grid(row=0, column=column, sticky="w", padx=(0, 24), pady=(0, 8))
        first_image = dfa_results[0].image_path
        rows = [("AFN", analysis.state_count, analysis.accepts_word,
                 first_image.parent / "afn.png" if first_image else None)]
        rows.extend((result.title, result.state_count, result.accepts_word, result.image_path) for result in dfa_results)
        for row, (title, state_count, accepted, image_path) in enumerate(rows, 1):
            ttk.Label(self.dfa_content, text=title, style="Body.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 24), pady=6)
            ttk.Label(self.dfa_content, text=str(state_count), style="Value.TLabel").grid(row=row, column=1, sticky="w", padx=(0, 24))
            ttk.Label(self.dfa_content, text="Sí" if accepted else "No", style="Value.TLabel", foreground=theme.GREEN if accepted else theme.RED).grid(row=row, column=2, sticky="w", padx=(0, 24))
            if image_path:
                ttk.Button(self.dfa_content, text="Ver grafo", command=lambda p=image_path, t=title: self._show_graph(p, t)).grid(row=row, column=3, sticky="e")
        if any(result.accepts_word != analysis.accepts_word for result in dfa_results):
            ttk.Label(self.dfa_content, text="Los autómatas dieron resultados distintos.", style="Body.TLabel", foreground=theme.RED).grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def _show_graph(self, path: Path, title: str) -> None:
        """Visor con desplazamiento horizontal y vertical, sin recortar el PNG."""
        try:
            picture = tk.PhotoImage(master=self.root, file=str(path))
        except (tk.TclError, OSError) as error:
            self._show_error(f"No fue posible abrir el grafo: {error}")
            return
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("1000x650")
        canvas = tk.Canvas(window, background="white", highlightthickness=0)
        horizontal = ttk.Scrollbar(window, orient="horizontal", command=canvas.xview)
        vertical = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        horizontal.grid(row=1, column=0, sticky="ew")
        vertical.grid(row=0, column=1, sticky="ns")
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        canvas.create_image(20, 20, image=picture, anchor="nw")
        canvas.image = picture
        canvas.configure(scrollregion=canvas.bbox("all"))
        window.bind("<Right>", lambda _event: canvas.xview_scroll(1, "pages"))
        window.bind("<Left>", lambda _event: canvas.xview_scroll(-1, "pages"))
        window.bind("<Next>", lambda _event: canvas.yview_scroll(1, "pages"))
        window.bind("<Prior>", lambda _event: canvas.yview_scroll(-1, "pages"))

    def load_file(self) -> None:
        """Procesa todo el archivo y permite inspeccionar cada resultado."""
        filename = filedialog.askopenfilename(
            title="Selecciona un archivo de expresiones",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return

        if self._batch_job is not None:
            self.root.after_cancel(self._batch_job)
            self._batch_job = None
        self._batch_results.clear()
        self.batch_table.delete(*self.batch_table.get_children())
        self._batch_word = self.word_var.get()
        self.batch_card.grid()
        displayed_word = repr(self._batch_word) if self._batch_word else "ε (vacía)"
        self.batch_context_var.set(f"{Path(filename).name} · Cadena: {displayed_word}")
        self._batch_iterator = iter_file_analyses(Path(filename), self._batch_word)
        self.file_var.set("Procesando archivo…")
        self._process_next_line()

    def _process_next_line(self) -> None:
        self._batch_job = None
        try:
            result = next(self._batch_iterator)
        except StopIteration:
            errors = sum(result.error is not None for result in self._batch_results.values())
            count = len(self._batch_results)
            summary = f"{count} {'línea' if count == 1 else 'líneas'}"
            if errors:
                summary += f" · {errors} {'error' if errors == 1 else 'errores'}"
            self.file_var.set(summary)
            return
        except (OSError, UnicodeError, ValueError) as error:
            self.file_var.set("No se pudo procesar el archivo")
            self._show_error(str(error))
            return
        identifier = str(result.line_number)
        self._batch_results[identifier] = result
        if result.error:
            values = (result.line_number, f"{result.expression} — {result.error}", "Error", "—", "—")
        else:
            verdicts = ["Sí" if accepted else "No" for accepted in (result.analysis.accepts_word, *(dfa.accepts_word for dfa in result.dfas))]
            values = (result.line_number, result.expression, *verdicts)
        self.batch_table.insert("", "end", iid=identifier, values=values)
        if len(self._batch_results) == 1:
            self.batch_table.selection_set(identifier)
            self._select_batch_result()
        self.file_var.set(f"{len(self._batch_results)} líneas procesadas…")
        self._batch_job = self.root.after(1, self._process_next_line)

    def _select_batch_result(self, _event=None) -> None:
        selected = self.batch_table.selection()
        if not selected:
            return
        result = self._batch_results.get(selected[0])
        if result is None:
            return
        self.expression_var.set(result.expression)
        self.word_var.set(self._batch_word)
        if result.error:
            self._show_error(f"Línea {result.line_number}: {result.error}")
        else:
            self._show_nfa_analysis(result.analysis, result.dfas)


def run() -> None:
    """Crea y muestra la ventana de la aplicación."""
    root = tk.Tk()
    LexerApp(root)
    root.mainloop()
