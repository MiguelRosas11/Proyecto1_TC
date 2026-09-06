"""Conversión y validación de expresiones regulares de un carácter por símbolo."""

OPERATORS = {"|", "*", ".", "(", ")"}
PRECEDENCE = {"|": 1, ".": 2, "*": 3}


def is_symbol(token: str) -> bool:
    """Indica si *token* representa un símbolo del alfabeto."""
    return len(token) == 1 and token not in OPERATORS and not token.isspace()


def validate_characters(expression: str) -> None:
    """Verifica las restricciones básicas antes de transformar la expresión."""
    if not expression:
        raise ValueError("La expresión regular no puede estar vacía.")

    for token in expression:
        if token.isspace():
            raise ValueError("La expresión regular no debe contener espacios.")
        if not (is_symbol(token) or token in OPERATORS):
            raise ValueError(f"Símbolo no permitido: {token!r}")
