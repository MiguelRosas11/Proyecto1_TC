"""Simulación de AFN mediante movimientos y epsilon-cerradura."""

from dataclasses import dataclass

from .models import EPSILON, NFA


@dataclass(frozen=True)
class SimulationStep:
    """Estados activos después de iniciar o de consumir un símbolo."""

    symbol: str | None
    states: frozenset[int]


def epsilon_closure(nfa: NFA, states: set[int]) -> set[int]:
    """Obtiene los estados alcanzables sin consumir símbolos."""
    closure = set(states)
    pending = list(states)

    while pending:
        state = pending.pop()
        destinations = nfa.transitions.get(state, {}).get(EPSILON, set())
        for destination in destinations:
            if destination not in closure:
                closure.add(destination)
                pending.append(destination)

    return closure


def move(nfa: NFA, states: set[int], symbol: str) -> set[int]:
    """Sigue todas las transiciones etiquetadas con un símbolo."""
    destinations: set[int] = set()
    for state in states:
        destinations.update(nfa.transitions.get(state, {}).get(symbol, set()))
    return destinations


def accepts(nfa: NFA, word: str) -> bool:
    """Indica si el AFN acepta la cadena completa ``word``."""
    steps = simulate(nfa, word)
    return bool(steps[-1].states & nfa.accept_states)


def simulate(nfa: NFA, word: str) -> tuple[SimulationStep, ...]:
    """Simula el AFN y conserva los conjuntos de estados para presentarlos."""
    if nfa.start_state is None:
        raise ValueError("El AFN no tiene estado inicial.")

    current_states = epsilon_closure(nfa, {nfa.start_state})
    steps = [SimulationStep(symbol=None, states=frozenset(current_states))]
    for symbol in word:
        current_states = epsilon_closure(nfa, move(nfa, current_states, symbol))
        steps.append(SimulationStep(symbol=symbol, states=frozenset(current_states)))

    return tuple(steps)
