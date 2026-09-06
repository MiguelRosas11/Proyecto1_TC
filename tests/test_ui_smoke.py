"""Comprobación ligera de que la interfaz puede construirse y analizar."""

import tkinter as tk
import unittest

from src.ui.app import LexerApp


class InterfaceSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"No hay pantalla disponible para Tkinter: {error}")
        self.root.withdraw()

    def tearDown(self) -> None:
        if hasattr(self, "root"):
            self.root.destroy()

    def test_window_analyzes_a_valid_word(self) -> None:
        app = LexerApp(self.root)
        app.expression_var.set("a*")
        app.word_var.set("aa")
        app.analyze()
        self.root.update_idletasks()

        visible_text = [child.cget("text") for child in app.status_content.winfo_children()]
        self.assertIn("Cadena aceptada", visible_text)


if __name__ == "__main__":
    unittest.main()
