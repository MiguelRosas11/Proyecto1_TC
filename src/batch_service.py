"""Análisis por línea, conservando resultados y gráficas independientes."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .analysis_service import AutomatonAnalysis, NFAAnalysis, analyze_nfa
from .dfa_pipeline import OUTPUT_DIR, analyze_dfas


@dataclass(frozen=True)
class LineAnalysis:
    line_number: int
    expression: str
    analysis: NFAAnalysis | None = None
    dfas: tuple[AutomatonAnalysis, ...] = ()
    error: str | None = None


def iter_file_analyses(path: Path, word: str, output_dir: Path | None = None):
    """Procesa cada línea no vacía con la misma cadena; un error no detiene el lote."""
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    if not any(line.strip() for line in lines):
        raise ValueError("El archivo no contiene expresiones regulares.")
    directory = Path(output_dir) if output_dir is not None else OUTPUT_DIR / f"lote_{uuid4().hex[:12]}"
    for number, line in enumerate(lines, 1):
        expression = line.strip()
        if not expression:
            continue
        try:
            analysis = analyze_nfa(expression, word)
            dfas = analyze_dfas(analysis.nfa, word, directory / f"linea_{number:03d}")
            yield LineAnalysis(number, expression, analysis, dfas)
        except (ValueError, RuntimeError, OSError) as error:
            yield LineAnalysis(number, expression, error=str(error))
