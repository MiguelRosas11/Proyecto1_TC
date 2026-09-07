# Analizador de expresiones regulares y autómatas

Proyecto 1 de Teoría de la Computación. Recibe una expresión regular `r` y una
cadena `w`, construye un AFN de Thompson, lo convierte a AFD por subconjuntos,
minimiza el AFD por refinamiento de particiones y simula los tres autómatas.
La interfaz indica **Sí / No** y permite abrir sus grafos.

## Instalación

Requiere **Python 3.10 o posterior**, Tkinter y Graphviz (ejecutable `dot`).
Los algoritmos están implementados en Python; Graphviz solo dibuja los grafos.
`re` se usa únicamente como referencia independiente en las pruebas.

1. Instalar Python con Tkinter. `python3 -m tkinter` debe abrir una ventana.
   En Linux puede requerirse el paquete `python3-tk`; en Windows, usar el
   instalador de Python con Tcl/Tk. En macOS, usar una distribución con Tkinter.
2. Instalar Graphviz y agregar su carpeta `bin` al `PATH`:
   - macOS con Homebrew: `brew install graphviz`.
   - Debian/Ubuntu: `sudo apt install graphviz`.
   - Windows: instalar Graphviz y agregar su carpeta `bin` al `PATH`.
3. Desde la raíz del proyecto:

```sh
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
dot -V
python main.py
```

En Windows, activar con `.venv\Scripts\activate` (cmd) o
`.venv\Scripts\Activate.ps1` (PowerShell). Si `python3` es 3.9, seleccionar
explícitamente un intérprete 3.10+ antes de crear el entorno.

## Uso y sintaxis

- `|`: unión; `*`: cerradura de Kleene; `(...)`: agrupación.
- Concatenación implícita (`ab`) o explícita (`a.b`).
- Precedencia: `*`, concatenación, `|`.
- `ε`: palabra vacía dentro de la expresión. Para evaluar la cadena vacía,
  **dejar vacío el campo de cadena**, no escribir el carácter `ε`.
- Cada símbolo del alfabeto es un carácter. Se deriva de la expresión y
  excluye operadores y `ε`. Se rechazan expresiones vacías o con espacios.
- No se implementa la sintaxis extendida de motores de regex: `+`, `?`,
  corchetes y barras invertidas son caracteres literales, no atajos ni escapes.
  Los operadores reservados no se pueden escapar para usarlos como literales.
- La aceptación requiere consumir **toda** la cadena. Un carácter ajeno al
  alfabeto se rechaza.

Ingresar una expresión y una cadena; pulsar **Analizar**. Los resultados aparecen después de analizar. La vista muestra
concatenación explícita, postfix, alfabeto, estados del AFN, epsilon-cerraduras
y veredictos de los dos AFD. Cada fila de la tabla **Autómatas** tiene un botón **Ver grafo** que abre
una ventana con desplazamiento horizontal y vertical. La flecha de entrada señala
el estado inicial y el doble círculo señala aceptación. En el AFD, cada estado
muestra el subconjunto de estados AFN que representa; `{}` es el estado muerto.

## Archivos de expresiones

**Cargar archivo .txt** procesa automáticamente cada línea no vacía con la
cadena que esté en el campo al iniciar la carga. Se acepta UTF-8 con o sin BOM.
Las líneas vacías se omiten y se conserva la numeración original. Una expresión
inválida aparece como error y no detiene las siguientes líneas.

La tabla muestra AFN, AFD y AFD mínimo por línea. Seleccionar una fila restaura
su expresión, cadena y resultados, con acceso a sus propias gráficas. Cambiar
el campo de cadena no recalcula el lote existente: cargar otra vez el archivo
para evaluarlo con una cadena distinta.

## Salidas

Análisis individual: `outputs/afn.png`, `outputs/afd.png`,
`outputs/afd_minimo.png`, con sus `.dot`. Se reemplazan al analizar de nuevo.
La carpeta se resuelve respecto del proyecto, independientemente de dónde se
inicie el programa.

Cada carga de archivo crea `outputs/lote_<identificador>/linea_NNN/`, con tres
PNG y tres DOT por expresión válida. Los lotes no se sobrescriben entre sí.
`outputs/` está excluido de Git; se puede limpiar cuando ya no se necesite.

## Arquitectura

| Módulo | Responsabilidad |
|---|---|
| `regex_utils.py` | Validación, concatenación y Shunting Yard |
| `thompson.py` | Construcción del AFN |
| `nfa_simulator.py` | Epsilon-cerradura, movimientos y simulación AFN |
| `subset_construction.py` | AFD completo y mapa de subconjuntos |
| `dfa_simulator.py` | Simulación del AFD original o mínimo |
| `dfa_minimizer.py` | Estados alcanzables y refinamiento de particiones |
| `renderer.py` | PNG/DOT con Graphviz |
| `dfa_pipeline.py` | Coordinación del bloque AFD y sus gráficas |
| `analysis_service.py` | Resultados para la interfaz |
| `batch_service.py` | Procesamiento por línea con errores independientes |
| `ui/` | Interfaz Tkinter y visor de imágenes |

El modelo `DFA` impide transiciones epsilon. La determinización incluye el
subconjunto vacío cuando es alcanzable; la minimización exige un AFD completo,
elimina estados inalcanzables y numera el estado inicial como `M0`.

## Validación

```sh
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Las pruebas verifican los algoritmos, equivalencia de los tres simuladores en
1,290 combinaciones de entrada frente a una referencia independiente, equivalencia
AFD/mínimo mediante exploración del producto, conteos mínimos conocidos y ausencia
de pares de estados equivalentes en los mínimos de prueba. También verifican
PNG reales, errores de Graphviz, lotes y acciones de la interfaz.

Las pruebas gráficas requieren `dot`; las de interfaz requieren Tkinter y una
sesión gráfica. Si Tk no puede crear una ventana, las pruebas de interfaz se
marcan como omitidas: eso no sustituye la demostración en un equipo con pantalla.

## Alcance y límites

Es un reconocedor de lenguajes regulares del curso: no tokeniza programas ni
implementa una herramienta de regex de propósito general. La determinización
puede crecer exponencialmente en estados; expresiones grandes pueden tardar y
producir grafos extensos. El lote permite actualizar la interfaz entre líneas,
pero el análisis de una sola expresión se ejecuta en el hilo de la interfaz.
