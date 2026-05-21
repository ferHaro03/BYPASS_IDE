# 📄 Informe Técnico: Aplicación de la Teoría de Lenguajes y Autómatas en BYPASS

## 1. Introducción al Lenguaje BYPASS
**BYPASS** es un Lenguaje de Dominio Específico (DSL) diseñado para la programación de interfaces y grafos de audio. Desde la perspectiva teórica de la computación, el desarrollo de BYPASS implica la construcción de un traductor que mapea una cadena de caracteres (código fuente) a una estructura ejecutable (grafo de procesamiento de señales). Para lograr esto, la arquitectura se divide en fases que corresponden directamente a la **Jerarquía de Chomsky**.

---

## 2. Nivel 1: Lenguajes Regulares y Autómatas Finitos (El Lexer)

El analizador léxico de BYPASS funciona como un reconocedor formal de un **Lenguaje Regular (Tipo 3)**. Su objetivo es particionar una cadena de entrada en una secuencia de componentes léxicos (Tokens) válidos según un alfabeto y un conjunto de reglas.

### 2.1 Expresiones Regulares como Especificación Completa
El alfabeto $\Sigma$ de BYPASS incluye todos los caracteres ASCII imprimibles. Las reglas del lenguaje se definen mediante las siguientes Expresiones Regulares (Regex), evaluadas en orden de prioridad (Regla del *Maximum Munch*):

| Token (Clase Léxica)     | Expresión Regular (Patrón)                                     | Descripción Técnica del Reconocimiento                                                                                    |
| :----------------------- | :------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `T_COMMENT`              | `#.*`                                                          | Inicia con `#` y consume cualquier carácter cero o más veces hasta el fin de línea.                                       |
| `T_ARROW`                | `->`                                                           | Secuencia literal estricta del guion y el símbolo de mayor que.                                                           |
| `T_NUMBER`               | `\d+(\.\d+)?(hz\|ms\|bpm\|db\|%)?`                             | Evalúa secuencias numéricas con soporte opcional para punto decimal y sufijos de magnitudes físicas del dominio de audio. |
| `T_STRING`               | `"[^"]*"`                                                      | Captura cadenas literales asegurando que no contengan comillas internas.                                                  |
| `T_ID`                   | `[a-zA-Z_][a-zA-Z0-9_]*`                                       | Inicia con letra o guion bajo, seguido de caracteres alfanuméricos. Estado de captura general para optimización.          |
| `T_NEWLINE`              | `                                                              |
| `                        | Carácter de control de salto de línea para rastreo de errores. |
| `T_SKIP`                 | `[ 	]+`                                                        | Captura y omite secuencias de uno o más espacios en blanco o tabulaciones.                                                |
| `T_EE`                   | `==`                                                           | Operador relacional de igualdad.                                                                                          |
| `T_GE` / `T_LE` / `T_NE` | `>=`, `<=`, `!=`                                               | Operadores relacionales compuestos.                                                                                       |
| `T_ASSIGN`               | `=`                                                            | Operador de asignación.                                                                                                   |
| `T_GT` / `T_LT`          | `>`, `<`                                                       | Operadores relacionales simples.                                                                                          |
| `Aritméticos`            | `\+`, `-`, `\*`, `/`                                           | Caracteres de escape requeridos (`\`) por ser meta-caracteres en Regex.                                                   |
| `Puntuación`             | `:`, `;`, `,`, `\.`                                            | Delimitadores estructurales y de acceso a miembros.                                                                       |
| `Agrupación`             | `\(`, `\)`, `\{`, `\}`, `\[`, `\]`                             | Delimitadores de bloques, parámetros y splitters de audio.                                                                |
| `T_MISMATCH`             | `.`                                                            | Sumidero lógico: Captura caracteres ilegales para el manejo de errores no bloqueantes.                                    |

**Optimización de Estados:**
En lugar de codificar palabras reservadas en el autómata principal, el Lexer reconoce el token genérico `T_ID` y consulta tablas hash en tiempo $O(1)$ para reclasificarlo en `T_FUNCTION`, `T_BUILTIN_MOD`, `T_USER_FUN` o `T_VAR_ID`.

               +-------------------------------------------+
               |             Estado Inicial q0             |
               +-------------------------------------------+
                                     |
                          [a-zA-Z_]  |
                                     v
               +-------------------------------------------+
               |              Estado q_ID                  | <---+ [a-zA-Z0-9_]
               +-------------------------------------------+ ----+
                                     |
                          Delimitador / Espacio
                                     v
               +-------------------------------------------+
               |      Fase de Consulta en Tabla Hash       |
               +-------------------------------------------+
                 /                 |                      \
  +--------------------+   +-----------------------+  +----------------------+         
  | Existe en KEYWORDS |   | Existe en BUILTIN_MOD |  | No existe (ID Local) |
  +--------------------+   +-----------------------+  +----------------------+
        /                           |                           \
       v                            v                            v      
  +--------------------+     +----------------------+      +---------------------------+             
  |  Emite T_FUNCTION, |     | Emite T_BUILTIN_MOD  |      |  Revisa primera letra:    |
  |  T_MONITOR, etc.   |     | (Gain, Filter, etc.) |      | - Mayúscula -> T_USER_FUN |
  +--------------------+     +----------------------+      | - Minúscula -> T_VAR_ID   |
                                                           +---------------------------+ 

### 2.2 Formalización del Autómata Finito Determinista (AFD)
El Lexer se define formalmente como el Autómata Finito Determinista $M = (Q, \Sigma, \delta, q_0, F)$, donde:
* **$Q$**: Conjunto finito de estados $\{q_0, q_1, q_2, ... q_n\}$.
* **$\Sigma$**: Alfabeto de entrada (Caracteres ASCII).
* **$q_0$**: Estado inicial.
* **$F$**: Conjunto de estados de aceptación.
* **$\delta$**: Función de transición $\delta(q, c) 
ightarrow q'$.

#### A. Grafo de Transición para el Token de Flujo (T_ARROW)
1. Estado inicial **$q_0$** lee `-`, transita a **$q_a$**.
2. Desde **$q_a$**, si lee `>`, transita al estado de aceptación **$q_{accept\_arrow}$** y emite `T_ARROW`.

#### B. Sub-Autómata Complejo: Magnitudes Físicas (T_NUMBER)
* **Paso 1 (Parte Entera):** $\delta(q_0, digit) = q_{int} 
ightarrow \delta(q_{int}, digit) = q_{int}$ (Bucle).
* **Paso 2 (Decimal):** $\delta(q_{int}, '.') = q_{dot} 
ightarrow \delta(q_{dot}, digit) = q_{dec} 
ightarrow \delta(q_{dec}, digit) = q_{dec}$.
* **Paso 3 (Unidades):** Si desde $q_{int}$ o $q_{dec}$ se recibe 'h', transita a $q_h$. $\delta(q_h, 'z') = q_{accept\_num}$ (Acepta `hz`).
* **Paso 4 (Aceptación):** Si se recibe espacio u operador, transita a $q_{accept\_num}$ asumiendo un escalar sin unidad.

#### C. Manejo del Estado Sumidero (Resiliencia)
BYPASS implementa tolerancia a fallos. La expresión regular `.` envía caracteres desconocidos al estado de aceptación $q_{error}$, emitiendo `T_MISMATCH`, registrando el error en consola, y reiniciando el autómata en $q_0$ sin bloquear el IDE.

---

## 3. Nivel 2: Gramáticas Libres de Contexto y Autómatas de Pila (El Parser)

Los tokens sueltos se estructuran lógicamente mediante **Lenguajes Libres de Contexto (Tipo 2)**.

### 3.1 Gramática Libre de Contexto (GLC)
Definida por la tupla $G = (V, \Sigma, R, S)$. En BYPASS, las reglas de ruteo permiten recursividad asociativa a la derecha:
* `Routing -> Atom ( -> Routing ) | \epsilon`
* `Atom -> T_INPUT | T_BUILTIN_MOD | T_VAR_ID`

### 3.2 Autómata de Pila mediante Descenso Recursivo
BYPASS implementa un **Parser de Descenso Recursivo** (Top-Down Parser). Utiliza la pila de llamadas del sistema operativo (*Call Stack*) para recordar el anidamiento. Al detectar un `->`, la función se llama a sí misma, dotando al Parser de la memoria de un **Autómata de Pila**.

### 3.3 El Árbol de Sintaxis Abstracta (AST)
Convierte el flujo lineal en un Grafo Dirigido (`AudioRouteNode` como conexiones binarias, `AtomicNode` como hojas), preparando el terreno para el ruteo de audio.

---

## 4. Nivel 3: Lenguajes Sensibles al Contexto (Análisis Semántico)

Corresponde a los **Lenguajes de Tipo 1**. El Autómata de Pila verifica que `A -> B` sea correcto estructuralmente, pero la Semántica valida el contexto mediante una Tabla de Símbolos:
1. **Tipado por Dominio:** Valida que un `Filter` reciba unidades `hz` y no `ms`.
2. **Resolución de Scope:** Mapeo de `T_VAR_ID` a instancias en memoria.
3. **Prevención de Feedback Loop:** Detección de grafos cíclicos prohibidos matemáticamente.

---

## 5. Conclusión de la Arquitectura
El compilador de BYPASS demuestra la aplicación directa de la abstracción matemática en software funcional. Al aislar las fases en Lexer (AFD), Parser (PDA/GLC) y Semántica (Contexto), se logra un análisis modular que permite validaciones en tiempo real dentro del IDE sin penalizar el rendimiento del motor de audio.