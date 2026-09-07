"""Exportación de los autómatas a DOT y PNG mediante Graphviz."""

from pathlib import Path

from graphviz import Digraph, escape
from graphviz.backend import ExecutableNotFound

from .models import DFA, NFA


def _render(automaton, output_dir, filename, title, state_labels, nondeterministic):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    graph = Digraph(name=filename, format="png")
    graph.attr(rankdir="LR", label=escape(title), labelloc="t", fontname="Helvetica", bgcolor="white")
    graph.attr("node", fontname="Helvetica")
    graph.attr("edge", fontname="Helvetica")
    graph.node("start", label="", shape="point")
    if automaton.start_state is not None:
        graph.edge("start", str(automaton.start_state))
    for state in sorted(automaton.states):
        label = state_labels.get(state, str(state))
        graph.node(str(state), label=escape(label), shape="doublecircle" if state in automaton.accept_states else "circle")
    edges = {}
    for source in sorted(automaton.states):
        for symbol, targets in sorted(automaton.transitions.get(source, {}).items()):
            for target in sorted(targets) if nondeterministic else [targets]:
                edges.setdefault((source, target), []).append(symbol)
    for (source, target), symbols in sorted(edges.items()):
        graph.edge(str(source), str(target), label=escape(", ".join(symbols)))
    try:
        path = graph.render(filename=f"{filename}.dot", directory=str(output_dir), cleanup=False)
    except ExecutableNotFound as error:
        raise RuntimeError("Falta Graphviz: instala el ejecutable dot y comprueba 'dot -V'.") from error
    # Graphviz añade .png al nombre .dot; exponemos los nombres acordados.
    destination = output_dir / f"{filename}.png"
    Path(path).replace(destination)
    return destination.resolve()


def render_nfa(nfa: NFA, output_dir: Path) -> Path:
    return _render(nfa, output_dir, "afn", "AFN de Thompson", {}, True)


def render_dfa(dfa: DFA, output_dir: Path, filename: str, title: str,
               state_labels: dict[int, str] | None = None) -> Path:
    labels = state_labels if state_labels is not None else {state: f"M{state}" for state in dfa.states}
    return _render(dfa, output_dir, filename, title, labels, False)
