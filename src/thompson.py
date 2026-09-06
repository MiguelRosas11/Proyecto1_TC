"""Construcción de Thompson: de una expresión postfix a un AFN."""

from .models import Fragment, NFA
from .regex_utils import is_symbol


class ThompsonBuilder:
    """Crea estados consecutivos mientras ensambla fragmentos de AFN."""

    def __init__(self) -> None:
        self.nfa = NFA()
        self._next_state = 0

    def new_state(self) -> int:
        state = self._next_state
        self._next_state += 1
        self.nfa.add_state(state)
        return state

    def symbol_fragment(self, symbol: str) -> Fragment:
        """Construye el fragmento elemental para un símbolo del alfabeto."""
        if not is_symbol(symbol):
            raise ValueError(f"No se puede crear un fragmento para {symbol!r}.")
        start = self.new_state()
        end = self.new_state()
        self.nfa.add_transition(start, symbol, end)
        return Fragment(start, end)
