"""Pruebas del procesamiento de expresiones, Thompson y simulación de AFN."""

import unittest

from src.nfa_simulator import accepts, epsilon_closure
from src.regex_utils import infix_to_postfix, insert_concatenation
from src.thompson import build_nfa


class RegexAndNFATests(unittest.TestCase):
    def test_concatenation_is_inserted_only_when_needed(self) -> None:
        self.assertEqual(insert_concatenation("(a|b)*abb"), "(a|b)*.a.b.b")

    def test_shunting_yard_respects_precedence(self) -> None:
        self.assertEqual(infix_to_postfix("a|bc*"), "abc*.")

    def test_invalid_expression_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            infix_to_postfix("a|")
        with self.assertRaises(ValueError):
            infix_to_postfix("(ab")

    def test_thompson_nfa_accepts_expected_language(self) -> None:
        nfa = build_nfa("(a|b)*abb(a|b)*")
        self.assertTrue(accepts(nfa, "babbaaaaa"))
        self.assertTrue(accepts(nfa, "abb"))
        self.assertFalse(accepts(nfa, "abababa"))

    def test_star_accepts_empty_word(self) -> None:
        nfa = build_nfa("a*")
        self.assertTrue(accepts(nfa, ""))
        self.assertTrue(nfa.accept_states & epsilon_closure(nfa, {nfa.start_state}))


if __name__ == "__main__":
    unittest.main()
