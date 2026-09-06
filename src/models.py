"""Estructuras de datos sencillas para los autómatas finitos."""

from dataclasses import dataclass, field


EPSILON = "ε"


@dataclass
class NFA:
    """Autómata finito no determinista con transiciones epsilon."""

    states: set[int] = field(default_factory=set)
    alphabet: set[str] = field(default_factory=set)
    start_state: int | None = None
    accept_states: set[int] = field(default_factory=set)
    transitions: dict[int, dict[str, set[int]]] = field(default_factory=dict)

    def add_state(self, state: int) -> None:
        self.states.add(state)
        self.transitions.setdefault(state, {})

    def add_transition(self, source: int, symbol: str, destination: int) -> None:
        """Agrega una transición y conserva todos los estados involucrados."""
        self.add_state(source)
        self.add_state(destination)
        self.transitions[source].setdefault(symbol, set()).add(destination)
        if symbol != EPSILON:
            self.alphabet.add(symbol)


@dataclass
class DFA:
    """Autómata finito determinista usado por los módulos de Persona B."""

    states: set[int] = field(default_factory=set)
    alphabet: set[str] = field(default_factory=set)
    start_state: int | None = None
    accept_states: set[int] = field(default_factory=set)
    transitions: dict[int, dict[str, int]] = field(default_factory=dict)

    def add_state(self, state: int) -> None:
        self.states.add(state)
        self.transitions.setdefault(state, {})

    def add_transition(self, source: int, symbol: str, destination: int) -> None:
        """Agrega una transición determinista para un símbolo del alfabeto."""
        if symbol == EPSILON:
            raise ValueError("Un AFD no puede tener transiciones epsilon.")
        self.add_state(source)
        self.add_state(destination)
        self.transitions[source][symbol] = destination
        self.alphabet.add(symbol)


@dataclass(frozen=True)
class Fragment:
    """Fragmento temporal de Thompson: una entrada y una salida."""

    start: int
    end: int
