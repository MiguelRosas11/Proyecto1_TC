"""Simulación determinista de una cadena completa."""

from .models import DFA


def accepts_dfa(dfa: DFA, word: str) -> bool:
    if dfa.start_state is None:
        raise ValueError("El AFD no tiene estado inicial.")
    state = dfa.start_state
    for symbol in word:
        if symbol not in dfa.alphabet:
            return False
        destination = dfa.transitions.get(state, {}).get(symbol)
        if destination is None:
            return False
        state = destination
    return state in dfa.accept_states
