import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.batch_service import iter_file_analyses


class BatchTests(unittest.TestCase):
    def test_every_line_continues_after_error_and_keeps_own_graphs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.txt"
            source.write_text("\ufeffa*\n\na|\na|b\na*\n", encoding="utf-8")
            results = list(iter_file_analyses(source, "aa", root / "graphs"))
            self.assertEqual([r.line_number for r in results], [1, 3, 4, 5])
            self.assertIsNotNone(results[1].error)
            self.assertTrue(results[0].analysis.accepts_word)
            self.assertFalse(results[2].analysis.accepts_word)
            self.assertTrue(results[3].analysis.accepts_word)
            paths = [r.dfas[0].image_path for r in results if not r.error]
            self.assertEqual(len(set(paths)), 3)
            self.assertTrue(all(path.is_file() for path in paths))

    def test_empty_file_and_invalid_encoding(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_text("\n  \n")
            with self.assertRaises(ValueError):
                list(iter_file_analyses(path, ""))
            path.write_bytes(b"\xff")
            with self.assertRaises(UnicodeError):
                list(iter_file_analyses(path, ""))
