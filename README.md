# Analizador léxico de expresiones regulares

Proyecto 1 de Teoría de la Computación. A partir de una expresión regular y
una cadena, el programa construye autómatas y determina si la cadena pertenece
al lenguaje descrito.

## Alcance

El proyecto usa solamente los algoritmos solicitados en el enunciado:

1. Conversión de infix a postfix con Shunting Yard.
2. Construcción de AFN mediante Thompson.
3. Simulación del AFN con epsilon-cerradura.
4. Construcción de AFD por subconjuntos.
5. Minimización del AFD.
6. Simulación y visualización de los tres autómatas.

Los símbolos del alfabeto son caracteres individuales. `|`, `*`, `(` y `)`
son operadores; la concatenación se escribe de forma implícita. El programa
usa `ε` internamente para transiciones vacías.

## Interfaz

La aplicación tendrá **una sola vista principal**, por lo que no es necesario
crear varias pantallas ni navegación compleja. Esa vista cambia entre tres
estados: inicial, resultado y error.

- Dos campos: expresión regular y cadena a evaluar.
- Un botón para cargar un archivo `.txt` de expresiones, una por línea.
- Un botón principal para ejecutar el análisis.
- Tarjetas de resultado para postfix, AFN, AFD y AFD mínimo.
- Un estado de aceptación claro: `Aceptada` o `No aceptada`.

La estética seguirá referencias visuales de iOS: fondo gris muy claro,
tarjetas blancas, espacio generoso, azul de acento y tipografía limpia. Se
implementará con Tkinter, incluido con Python, para evitar dependencias de UI.

## Arquitectura

```text
Proyecto1/
├── main.py                       # Punto de entrada de la interfaz (Persona A)
├── README.md                     # Guía, arquitectura y uso (Persona A)
├── src/
│   ├── models.py                 # Contratos NFA/DFA compartidos, no editar después
│   ├── regex_utils.py            # Validación, concatenación, postfix (Persona A)
│   ├── thompson.py               # Construcción del AFN (Persona A)
│   ├── nfa_simulator.py          # Epsilon-cerradura y simulación AFN (Persona A)
│   ├── analysis_service.py       # Resultado del bloque AFN para la UI (Persona A)
│   ├── ui/                       # Interfaz y estilo (Persona A)
│   ├── subset_construction.py    # AFN a AFD (Persona B)
│   ├── dfa_minimizer.py          # Minimización de AFD (Persona B)
│   ├── dfa_simulator.py          # Simulación AFD (Persona B)
│   ├── dfa_pipeline.py           # Adaptador de resultados AFD para la UI (Persona B)
│   └── renderer.py               # Imágenes DOT/PNG de autómatas (Persona B)
├── tests/
│   ├── test_regex_and_nfa.py     # Pruebas de Persona A
│   └── test_dfa_and_graphs.py    # Pruebas de Persona B
├── inputs/                       # Archivos de expresiones de prueba
└── outputs/                      # Imágenes generadas; ignorado por Git
```

`models.py` define el contrato común: un autómata tiene estados, alfabeto,
estado inicial, estados de aceptación y transiciones. Cada módulo recibe una
estructura y devuelve otra; no imprime ni abre ventanas por cuenta propia.

## División del trabajo

### Persona A — interfaz y bloque AFN

- `models.py`, `regex_utils.py`, `thompson.py` y `nfa_simulator.py`.
- `analysis_service.py`, `main.py` y toda la carpeta `src/ui/`.
- `README.md` y `tests/test_regex_and_nfa.py`.
- Integración visual de los resultados que entregue `dfa_pipeline.py`.

### Persona B — bloque AFD y gráficas

- `subset_construction.py`, `dfa_minimizer.py` y `dfa_simulator.py`.
- `dfa_pipeline.py`, que expone los resultados AFD en el formato acordado.
- `renderer.py` y `tests/test_dfa_and_graphs.py`.
- Generación de los PNG/DOT para AFN, AFD y AFD mínimo.

El reparto queda equilibrado: Persona A desarrolla la transformación,
simulación no determinista y toda la experiencia visual; Persona B desarrolla
la determinización, minimización y las gráficas solicitadas.

### Regla para no interferir

Cada persona trabaja exclusivamente en sus archivos. Antes de que Persona B
empiece, Persona A congela `models.py`. Persona B no modifica `main.py`,
`README.md` ni `src/ui/`; Persona A no modifica los módulos de AFD ni
`renderer.py`. Se trabaja en ramas separadas y se integra mediante pull request
o merge una vez que pasen las pruebas.

## Contrato para la integración

Persona B implementará una función en `src/dfa_pipeline.py`:

```python
def analyze_dfas(nfa, word):
    """Devuelve los resultados del AFD por subconjuntos y del AFD mínimo."""
```

Cada resultado debe contener al menos `state_count`, `accepts_word` y una ruta
opcional a la imagen generada. La interfaz funciona desde ahora con el AFN y
mostrará las tarjetas AFD automáticamente al estar disponible ese módulo.

## Ejecución y pruebas

```text
python main.py
python -m unittest discover -s tests -v
```

En Windows, si `python` apunta a la Microsoft Store, use el intérprete de
Python instalado en su equipo o active el entorno virtual del proyecto.
