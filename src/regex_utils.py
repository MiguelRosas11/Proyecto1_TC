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


def insert_concatenation(expression: str) -> str:
    """Inserta el operador interno ``.`` donde la concatenación es implícita."""
    validate_characters(expression)
    result: list[str] = []

    for index, token in enumerate(expression):
        result.append(token)
        if index == len(expression) - 1:
            continue

        next_token = expression[index + 1]
        left_can_end = is_symbol(token) or token in {")", "*"}
        right_can_start = is_symbol(next_token) or next_token == "("
        if left_can_end and right_can_start:
            result.append(".")

    return "".join(result)


def infix_to_postfix(expression: str) -> str:
    """Convierte una expresión infija a postfix con Shunting Yard.

    La concatenación se vuelve explícita automáticamente antes de aplicar el
    algoritmo. Se rechazan expresiones con operadores o paréntesis mal usados.
    """
    expression = insert_concatenation(expression)
    output: list[str] = []
    operators: list[str] = []
    expecting_operand = True

    for token in expression:
        if is_symbol(token):
            if not expecting_operand:
                raise ValueError("Falta un operador entre símbolos.")
            output.append(token)
            expecting_operand = False
        elif token == "(":
            if not expecting_operand:
                raise ValueError("Falta concatenación antes de '('.")
            operators.append(token)
        elif token == ")":
            if expecting_operand:
                raise ValueError("Paréntesis de cierre sin una expresión previa.")
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            if not operators:
                raise ValueError("Paréntesis desbalanceados.")
            operators.pop()
            expecting_operand = False
        elif token == "*":
            if expecting_operand:
                raise ValueError("'*' debe seguir a un símbolo o a ')'.")
            output.append(token)
        else:  # | o .
            if expecting_operand:
                raise ValueError(f"El operador {token!r} no tiene operando izquierdo.")
            while (
                operators
                and operators[-1] != "("
                and PRECEDENCE[operators[-1]] >= PRECEDENCE[token]
            ):
                output.append(operators.pop())
            operators.append(token)
            expecting_operand = True

    if expecting_operand:
        raise ValueError("La expresión termina con un operador.")

    while operators:
        token = operators.pop()
        if token == "(":
            raise ValueError("Paréntesis desbalanceados.")
        output.append(token)

    return "".join(output)
