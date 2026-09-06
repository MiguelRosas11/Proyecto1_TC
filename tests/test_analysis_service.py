"""Pruebas del adaptador entre el AFN y la interfaz gráfica."""

import unittest

from src.analysis_service import analyze_nfa, analyze_optional_dfas
from src.models import DFA, EPSILON


class AnalysisServiceTests(unittest.TestCase):
    def test_analysis_contains_the_values_needed_by_the_interface(self) -> None:
        analysis = analyze_nfa("a*", "aa")

        self.assertEqual(analysis.explicit_expression, "a*")
        self.assertEqual(analysis.postfix, "a*")
        self.assertTrue(analysis.accepts_word)
        self.assertEqual(analysis.alphabet, ("a",))
        self.assertEqual(len(analysis.trace), 3)
        self.assertEqual(analysis.state_count, len(analysis.nfa.states))

    def test_optional_dfa_section_is_empty_until_partner_module_exists(self) -> None:
        analysis = analyze_nfa("a", "a")
        self.assertEqual(analyze_optional_dfas(analysis.nfa, analysis.word), ())

    def test_dfa_contract_rejects_epsilon_transitions(self) -> None:
        dfa = DFA()
        with self.assertRaises(ValueError):
            dfa.add_transition(0, EPSILON, 1)


if __name__ == "__main__":
    unittest.main()
