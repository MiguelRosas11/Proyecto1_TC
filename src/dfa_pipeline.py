"""Coordinación de determinización, minimización, simulaciones y gráficas."""

from pathlib import Path

from .analysis_service import AutomatonAnalysis
from .dfa_minimizer import minimize_dfa
from .dfa_simulator import accepts_dfa
from .renderer import render_dfa, render_nfa
from .subset_construction import build_dfa


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def analyze_dfas(nfa, word: str, output_dir: Path | None = None) -> tuple[AutomatonAnalysis, ...]:
    output_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
    construction = build_dfa(nfa)
    dfa = construction.dfa
    minimized = minimize_dfa(dfa)
    render_nfa(nfa, output_dir)
    dfa_image = render_dfa(dfa, output_dir, "afd", "AFD por subconjuntos", {
        state: f"D{state}\n{{{','.join(map(str, sorted(subset)))}}}"
        for state, subset in construction.state_subsets.items()
    })
    minimized_image = render_dfa(minimized, output_dir, "afd_minimo", "AFD mínimo")
    return (
        AutomatonAnalysis("AFD por subconjuntos", len(dfa.states), accepts_dfa(dfa, word), dfa_image),
        AutomatonAnalysis("AFD mínimo", len(minimized.states), accepts_dfa(minimized, word), minimized_image),
    )
