"""Adaptadores entre los algoritmos de autómatas y la interfaz gráfica."""

from dataclasses import dataclass
from pathlib import Path

from .nfa_simulator import SimulationStep, simulate
from .regex_utils import infix_to_postfix, insert_concatenation
from .thompson import build_nfa


@dataclass(frozen=True)
class AutomatonAnalysis:
    """Resumen visual que la interfaz puede mostrar para cualquier autómata."""

    title: str
    state_count: int
    accepts_word: bool
    image_path: Path | None = None


@dataclass(frozen=True)
class NFAAnalysis:
    """Resultado completo de la parte AFN del análisis."""

    expression: str
    explicit_expression: str
    postfix: str
    word: str
    state_count: int
    alphabet: tuple[str, ...]
    accepts_word: bool
    trace: tuple[SimulationStep, ...]


def analyze_nfa(expression: str, word: str) -> NFAAnalysis:
    """Ejecuta las transformaciones y la simulación necesarias para el AFN."""
    explicit_expression = insert_concatenation(expression)
    postfix = infix_to_postfix(expression)
    nfa = build_nfa(expression)
    trace = simulate(nfa, word)

    return NFAAnalysis(
        expression=expression,
        explicit_expression=explicit_expression,
        postfix=postfix,
        word=word,
        state_count=len(nfa.states),
        alphabet=tuple(sorted(nfa.alphabet)),
        accepts_word=bool(trace[-1].states & nfa.accept_states),
        trace=trace,
    )


def analyze_optional_dfas(nfa, word: str) -> tuple[AutomatonAnalysis, ...]:
    """Carga el aporte de AFD cuando esté integrado, sin bloquear la interfaz.

    Persona B implementará ``dfa_pipeline.analyze_dfas`` y devolverá una tupla
    de ``AutomatonAnalysis`` para el AFD por subconjuntos y el AFD mínimo.
    """
    try:
        from .dfa_pipeline import analyze_dfas
    except ModuleNotFoundError as error:
        if error.name in {"src.dfa_pipeline", "dfa_pipeline"}:
            return ()
        raise

    return tuple(analyze_dfas(nfa, word))
