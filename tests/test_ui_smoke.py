"""Comprobación ligera de que la interfaz puede construirse y analizar."""

import tkinter as tk
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.ui.app import LexerApp


class InterfaceSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"No hay pantalla disponible para Tkinter: {error}")
        self.root.withdraw()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output_patch = patch("src.dfa_pipeline.OUTPUT_DIR", Path(self.temp.name) / "graphs")
        self.output_patch.start()
        self.addCleanup(self.output_patch.stop)
        self.batch_patch = patch("src.batch_service.OUTPUT_DIR", Path(self.temp.name) / "batches")
        self.batch_patch.start()
        self.addCleanup(self.batch_patch.stop)

    def tearDown(self) -> None:
        if hasattr(self, "root"):
            self.root.destroy()

    def test_window_analyzes_a_valid_word(self) -> None:
        app = LexerApp(self.root)
        self.assertEqual(app.status_card.winfo_manager(), "")
        self.assertEqual(app.batch_card.winfo_manager(), "")
        app.expression_var.set("a*")
        app.word_var.set("aa")
        app.analyze()
        self.root.update_idletasks()

        visible_text = [child.cget("text") for child in app.status_content.winfo_children()]
        self.assertIn("Cadena aceptada", visible_text)
        self.assertEqual(app.status_card.winfo_manager(), "grid")
        self.assertEqual(app.dfa_card.winfo_manager(), "grid")

    def test_graph_viewer_loads_png_and_dfa_results_are_visible(self):
        app = LexerApp(self.root)
        app.expression_var.set("a*")
        app.word_var.set("")
        app.analyze()
        labels = [child.cget("text") for child in app.dfa_content.winfo_children() if "text" in child.keys()]
        self.assertEqual(labels.count("Sí"), 3)
        self.assertEqual(labels.count("Ver grafo"), 3)
        self.assertIn("1", labels)
        app._show_graph(Path(self.temp.name) / "graphs" / "afd_minimo.png", "Prueba")
        windows = [child for child in self.root.winfo_children() if isinstance(child, tk.Toplevel)]
        self.assertEqual(len(windows), 1)
        canvas = next(child for child in windows[0].winfo_children() if isinstance(child, tk.Canvas))
        self.assertGreater(canvas.image.width(), 0)

    def test_loading_file_processes_every_line_and_selection_restores_results(self):
        app = LexerApp(self.root)
        app.word_var.set("aa")
        source = Path(self.temp.name) / "demo.txt"
        source.write_text("a*\na|\na|b\n")
        with patch("src.ui.app.filedialog.askopenfilename", return_value=str(source)):
            app.load_file()
        while app._batch_job is not None:
            self.root.after_cancel(app._batch_job)
            app._process_next_line()
        self.assertEqual(len(app.batch_table.get_children()), 3)
        self.assertEqual(app.file_var.get(), "3 líneas · 1 error")
        self.assertIn("demo.txt", app.batch_context_var.get())
        self.assertIn("aa", app.batch_context_var.get())
        app.batch_table.selection_set("3")
        app._select_batch_result()
        self.assertEqual(app.expression_var.get(), "a|b")
        labels = [child.cget("text") for child in app.status_content.winfo_children()]
        self.assertIn("Cadena no aceptada", labels)
        app.batch_table.selection_set("2")
        app._select_batch_result()
        self.assertTrue(any("Línea 2" in child.cget("text") for child in app.status_content.winfo_children()))

    def test_bad_input_clears_previous_success_and_application_recovers(self):
        app = LexerApp(self.root)
        app.expression_var.set("a|")
        app.analyze()
        self.assertIn("La expresión termina con un operador.", [child.cget("text") for child in app.status_content.winfo_children()])
        self.assertEqual(app.dfa_card.winfo_manager(), "")
        app.expression_var.set("a")
        app.word_var.set("a")
        app.analyze()
        self.assertIn("Cadena aceptada", [child.cget("text") for child in app.status_content.winfo_children()])


if __name__ == "__main__":
    unittest.main()
