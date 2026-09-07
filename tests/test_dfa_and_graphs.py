"""Verificación de lenguaje, minimalidad real e imágenes generadas."""

import itertools
import re
import unittest
from collections import deque
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from graphviz.backend import ExecutableNotFound

from src.dfa_minimizer import minimize_dfa
from src.dfa_pipeline import analyze_dfas
from src.dfa_simulator import accepts_dfa
from src.models import DFA
from src.nfa_simulator import accepts
from src.renderer import render_nfa
from src.subset_construction import build_dfa
from src.thompson import build_nfa


def equivalent(left, right):
    """Explora el producto completo: busca un contraejemplo de cualquier longitud."""
    queue = deque([(left.start_state, right.start_state)])
    visited = set(queue)
    while queue:
        a, b = queue.popleft()
        if (a in left.accept_states) != (b in right.accept_states):
            return False
        for symbol in left.alphabet | right.alphabet:
            pair = (left.transitions.get(a, {}).get(symbol), right.transitions.get(b, {}).get(symbol))
            if pair not in visited:
                visited.add(pair)
                queue.append(pair)
    return True


class DFAAndGraphTests(unittest.TestCase):
    def test_complete_dfa_includes_empty_subset(self):
        result = build_dfa(build_nfa("ab"))
        self.assertIn(frozenset(), result.state_subsets.values())
        for state in result.dfa.states:
            self.assertEqual(set(result.dfa.transitions[state]), result.dfa.alphabet)
        self.assertNotIn("ε", result.dfa.alphabet)

    def test_three_simulators_match_independent_regex_oracle(self):
        expressions = ["a", "ab", "a|b", "a*", "(a|b)*abb(a|b)*", "(ab|ba)*", "a(b|a)*", "ε", "a|ε", "(ε|a)*b"]
        words = ["".join(word) for length in range(7) for word in itertools.product("ab", repeat=length)] + ["c", "ε"]
        for expression in expressions:
            nfa = build_nfa(expression)
            dfa = build_dfa(nfa).dfa
            minimized = minimize_dfa(dfa)
            self.assertTrue(equivalent(dfa, minimized), expression)
            for word in words:
                with self.subTest(expression=expression, word=word):
                    expected = re.fullmatch(expression.replace("ε", "(?:)"), word) is not None
                    self.assertEqual(accepts(nfa, word), expected)
                    self.assertEqual(accepts_dfa(dfa, word), expected)
                    self.assertEqual(accepts_dfa(minimized, word), expected)

    def test_known_minimal_state_counts_and_no_equivalent_pairs(self):
        for expression, count in (("a*", 1), ("a|b", 3), ("ab", 4), ("(a|b)*abb(a|b)*", 4), ("ε", 1)):
            dfa = build_dfa(build_nfa(expression)).dfa
            minimized = minimize_dfa(dfa)
            self.assertEqual(len(minimized.states), count, expression)
            self.assertLessEqual(len(minimized.states), len(dfa.states))
            for a, b in itertools.combinations(minimized.states, 2):
                left = DFA(minimized.states, minimized.alphabet, a, minimized.accept_states, minimized.transitions)
                right = DFA(minimized.states, minimized.alphabet, b, minimized.accept_states, minimized.transitions)
                self.assertFalse(equivalent(left, right), (expression, a, b))

    def test_unreachable_states_are_removed(self):
        dfa = DFA(states={0, 1}, alphabet={"a"}, start_state=0, accept_states={0}, transitions={0: {"a": 0}, 1: {"a": 1}})
        self.assertEqual(len(minimize_dfa(dfa).states), 1)
        self.assertEqual(dfa.states, {0, 1})

    def test_empty_language_and_partial_dfa(self):
        dfa = DFA(states={0}, alphabet={"a"}, start_state=0, transitions={0: {"a": 0}})
        self.assertFalse(accepts_dfa(minimize_dfa(dfa), ""))
        dfa.transitions[0].clear()
        self.assertFalse(accepts_dfa(dfa, "a"))
        with self.assertRaises(ValueError):
            minimize_dfa(dfa)
        with self.assertRaises(ValueError):
            accepts_dfa(DFA(), "")

    def test_pipeline_generates_three_valid_pngs_and_dot_annotations(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            results = analyze_dfas(build_nfa("a|ε"), "", path)
            self.assertEqual([r.title for r in results], ["AFD por subconjuntos", "AFD mínimo"])
            self.assertTrue(all(r.accepts_word for r in results))
            for name in ("afn", "afd", "afd_minimo"):
                self.assertEqual((path / f"{name}.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                dot = (path / f"{name}.dot").read_text()
                self.assertIn("start ->", dot)
                self.assertIn("doublecircle", dot)
            self.assertIn("ε", (path / "afn.dot").read_text())

    def test_graph_labels_escape_special_characters(self):
        with TemporaryDirectory() as directory:
            for symbol in ('"', "\\", "<", "&"):
                self.assertTrue(render_nfa(build_nfa(symbol), Path(directory)).is_file())

    def test_missing_graphviz_has_actionable_error(self):
        with TemporaryDirectory() as directory, patch("src.renderer.Digraph.render", side_effect=ExecutableNotFound(["dot"])):
            with self.assertRaisesRegex(RuntimeError, "dot -V"):
                render_nfa(build_nfa("a"), Path(directory))
