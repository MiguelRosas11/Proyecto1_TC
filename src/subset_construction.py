"""Determinización mediante epsilon-cerradura y construcción por subconjuntos."""

from collections import deque
from dataclasses import dataclass

from .models import DFA, NFA
from .nfa_simulator import epsilon_closure, move


@dataclass(frozen=True)
class SubsetConstructionResult:
    dfa: DFA
    state_subsets: dict[int, frozenset[int]]


def build_dfa(nfa: NFA) -> SubsetConstructionResult:
    """Construye un AFD completo, incluyendo el subconjunto vacío si se alcanza."""
    if nfa.start_state is None:
        raise ValueError("El AFN no tiene estado inicial.")
    initial = frozenset(epsilon_closure(nfa, {nfa.start_state}))
    identifiers = {initial: 0}
    pending = deque([initial])
    dfa = DFA(alphabet=set(nfa.alphabet), start_state=0)
    dfa.add_state(0)
    while pending:
        subset = pending.popleft()
        source = identifiers[subset]
        if subset & nfa.accept_states:
            dfa.accept_states.add(source)
        for symbol in sorted(nfa.alphabet):
            target = frozenset(epsilon_closure(nfa, move(nfa, set(subset), symbol)))
            if target not in identifiers:
                identifiers[target] = len(identifiers)
                pending.append(target)
            dfa.add_transition(source, symbol, identifiers[target])
    return SubsetConstructionResult(dfa, {state: subset for subset, state in identifiers.items()})
