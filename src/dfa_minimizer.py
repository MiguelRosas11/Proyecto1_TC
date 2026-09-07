"""Minimización por refinamiento de particiones de estados alcanzables."""

from collections import deque

from .models import DFA


def minimize_dfa(dfa: DFA) -> DFA:
    """Minimiza un AFD completo sin modificar el original."""
    if dfa.start_state not in dfa.states:
        raise ValueError("El AFD no tiene un estado inicial válido.")
    alphabet = sorted(dfa.alphabet)
    reachable = {dfa.start_state}
    pending = [dfa.start_state]
    while pending:
        state = pending.pop()
        for symbol in alphabet:
            target = dfa.transitions.get(state, {}).get(symbol)
            if target not in dfa.states:
                raise ValueError("La minimización requiere un AFD completo.")
            if target not in reachable:
                reachable.add(target)
                pending.append(target)

    partitions = [group for group in (reachable & dfa.accept_states, reachable - dfa.accept_states) if group]
    while True:
        membership = {state: index for index, group in enumerate(partitions) for state in group}
        refined = []
        for group in partitions:
            buckets = {}
            for state in sorted(group):
                signature = tuple(membership[dfa.transitions[state][symbol]] for symbol in alphabet)
                buckets.setdefault(signature, set()).add(state)
            refined.extend(buckets.values())
        if len(refined) == len(partitions):
            break
        partitions = refined

    # Numeración reproducible: el grupo inicial es M0 y los demás se recorren en BFS.
    initial_group = membership[dfa.start_state]
    identifiers = {initial_group: 0}
    queue = deque([initial_group])
    minimized = DFA(alphabet=set(alphabet), start_state=0)
    while queue:
        group_index = queue.popleft()
        source = identifiers[group_index]
        group = partitions[group_index]
        minimized.add_state(source)
        if group & dfa.accept_states:
            minimized.accept_states.add(source)
        representative = min(group)
        for symbol in alphabet:
            target_group = membership[dfa.transitions[representative][symbol]]
            if target_group not in identifiers:
                identifiers[target_group] = len(identifiers)
                queue.append(target_group)
            minimized.add_transition(source, symbol, identifiers[target_group])
    return minimized
