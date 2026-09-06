"""Construcción de Thompson: de una expresión postfix a un AFN."""

from .models import EPSILON, Fragment, NFA
from .regex_utils import infix_to_postfix, is_symbol


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

    def concatenate(self, left: Fragment, right: Fragment) -> Fragment:
        self.nfa.add_transition(left.end, EPSILON, right.start)
        return Fragment(left.start, right.end)

    def alternate(self, left: Fragment, right: Fragment) -> Fragment:
        start = self.new_state()
        end = self.new_state()
        self.nfa.add_transition(start, EPSILON, left.start)
        self.nfa.add_transition(start, EPSILON, right.start)
        self.nfa.add_transition(left.end, EPSILON, end)
        self.nfa.add_transition(right.end, EPSILON, end)
        return Fragment(start, end)

    def star(self, fragment: Fragment) -> Fragment:
        start = self.new_state()
        end = self.new_state()
        self.nfa.add_transition(start, EPSILON, fragment.start)
        self.nfa.add_transition(start, EPSILON, end)
        self.nfa.add_transition(fragment.end, EPSILON, fragment.start)
        self.nfa.add_transition(fragment.end, EPSILON, end)
        return Fragment(start, end)


def build_nfa(expression: str) -> NFA:
    """Construye un AFN de Thompson para una expresión regular infija."""
    builder = ThompsonBuilder()
    fragments: list[Fragment] = []

    for token in infix_to_postfix(expression):
        if is_symbol(token):
            fragments.append(builder.symbol_fragment(token))
        elif token == "*":
            if not fragments:
                raise ValueError("Postfix inválida: '*' sin operando.")
            fragments.append(builder.star(fragments.pop()))
        else:
            if len(fragments) < 2:
                raise ValueError(f"Postfix inválida: {token!r} sin dos operandos.")
            right = fragments.pop()
            left = fragments.pop()
            operation = builder.concatenate if token == "." else builder.alternate
            fragments.append(operation(left, right))

    if len(fragments) != 1:
        raise ValueError("La expresión no produjo un único AFN.")

    final_fragment = fragments.pop()
    builder.nfa.start_state = final_fragment.start
    builder.nfa.accept_states = {final_fragment.end}
    return builder.nfa
