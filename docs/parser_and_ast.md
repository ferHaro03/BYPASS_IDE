# 🌳 Documentación del Analizador Sintáctico (Parser) y AST

## 1. Visión General
El **Parser** (Analizador Sintáctico) es la segunda fase del compilador de BYPASS. Su responsabilidad es recibir la lista de tokens planos generada por el Lexer y organizarlos en una estructura jerárquica llamada **Árbol de Sintaxis Abstracta (AST)**. 

Si el Lexer verifica que las "palabras" existan, el Parser verifica que las "oraciones" tengan sentido gramatical.

## 2. Nodos del Árbol de Sintaxis Abstracta (AST)
El Parser de BYPASS traduce el código en los siguientes nodos lógicos:

* **`ProgramNode`**: El nodo raíz que contiene todas las sentencias del script.
* **`AudioRouteNode`**: Representa una conexión de audio (`A -> B`).
* **`SplitterNode`**: Representa procesamiento paralelo (`[Rama1, Rama2]`).
* **`ModuleCallNode`**: Llamada a un módulo nativo con parámetros (`Filter(cutoff: 500hz)`).
* **`FunctionDeclNode`**: Declaración de un efecto personalizado (`function MiEfecto(...)`).
* **`AssignmentNode`**: Asignación de variables (`target = valor`).
* **`UILayoutNode`**: Bloque de declaración de interfaz gráfica (`ui_layout { ... }`).
* **`IfNode` & `ConditionNode`**: Estructuras de control lógico.

### 3.1 Catálogo de Errores Sintácticos (Detectados por el Parser)

Los errores sintácticos ocurren cuando los tokens son válidos (el Lexer los reconoció), pero están organizados en un orden que viola las reglas de producción de la Gramática Libre de Contexto (GLC) de BYPASS. 

El método `eat(token_esperado)` del autómata de pila es el encargado de disparar estas excepciones.

#### 1. Formato de Parámetros Incorrecto (Missing Colon)
BYPASS exige argumentos nombrados estrictos.
* **Código Erróneo:** `Filter(cutoff, 500hz)` o `Gain(0.5)`
* **Lo que ve el Parser:** `T_VAR_ID T_COMMA` o `T_NUMBER`
* **Excepción disparada:** `Se esperaba T_COLON pero se encontró T_COMMA`. El autómata exige la estructura `T_VAR_ID -> T_COLON -> Valor`.

#### 2. Nodos de Ruteo Inválidos (Invalid Atom)
El operador de ruteo (`->`) requiere obligatoriamente un componente de audio a ambos lados.
* **Código Erróneo:** `INPUT -> -> OUTPUT` o `INPUT -> + -> OUTPUT`
* **Lo que ve el Parser:** `T_ARROW` seguido de otro `T_ARROW` o un operador aritmético.
* **Excepción disparada:** `Esperaba Nodo de Audio, encontré '->'`.

#### 3. Desbalance de Delimitadores (Unmatched Brackets/Braces)
Ocurre cuando el usuario olvida cerrar bloques lógicos, funciones o arreglos de procesamiento paralelo (Splitters).
* **Código Erróneo:** `INPUT -> [Filter, Delay -> OUTPUT`
* **Lo que ve el Parser:** Llega el token `T_ARROW` cuando la regla del Splitter exigía un `T_COMMA` o un `T_RBRACKET` (`]`).
* **Excepción disparada:** `Se esperaba T_RBRACKET pero se encontró T_ARROW`.

#### 4. Objetivo de Asignación Inválido (Invalid L-Value)
El operador de asignación (`=`) requiere estrictamente que el lado izquierdo sea un identificador de variable (`T_VAR_ID`).
* **Código Erróneo:** `500hz = Filter(cutoff: 500hz)` o `Gain = Fuzz(...)`
* **Lo que ve el Parser:** Un `T_NUMBER` o un `T_BUILTIN_MOD` seguido de un `T_ASSIGN`.
* **Excepción disparada:** El parser falla al intentar evaluar esto como una sentencia de inicio, marcando error de sentencia no reconocida.

#### 5. Estructuras de Control Malformadas
Olvidar los elementos obligatorios en un bloque `if` o `ui_layout`.
* **Código Erróneo:** `if bypass == true { INPUT -> OUTPUT }` (Faltan paréntesis).
* **Lo que ve el Parser:** `T_IF` seguido de un `T_VAR_ID`.
* **Excepción disparada:** `Se esperaba T_LPAREN pero se encontró T_VAR_ID`. El Parser exige que la condición del `if` esté envuelta en `()`.

## 3. Manejo de Errores Sintácticos (Modo Pánico)
El Parser implementa un sistema de recuperación de errores conocido como **Panic Mode**. 
Cuando el usuario comete un error de escritura (ej. olvidar un paréntesis o dos puntos `:`), el compilador no se detiene abruptamente. Atrapa la excepción, la registra en la consola de errores y utiliza el método `synchronize()` para saltar tokens hasta encontrar una nueva línea segura, permitiendo que el IDE analice el resto del código sin congelarse.

---

## 4. Frontera con el Análisis Semántico
El Parser asegura que la estructura gramatical sea perfecta, pero **no comprende el significado físico o lógico del código**. Una sentencia puede ser sintácticamente correcta pero **semánticamente inválida**.

El AST generado por este Parser será consumido por el Analizador Semántico (Fase 3) para detectar los siguientes **Errores Semánticos**:

### A. Incompatibilidad de Dominio (Type Mismatch)
Ocurre cuando se asigna un valor a un parámetro que espera una magnitud física diferente.
* **Sintácticamente válido:** `Filter(cutoff: 50ms)` (El Parser solo ve `ID(ID: NUMBER)`).
* **Error Semántico:** El parámetro `cutoff` del filtro exige una frecuencia (`hz`), pero recibió un tiempo (`ms`).

### B. Violación de Ámbito (Scope / Undeclared Variables)
Ocurre al intentar usar o rutear una señal que no existe en el contexto actual.
* **Sintácticamente válido:** `INPUT -> mi_fuzz_fantasma -> OUTPUT`
* **Error Semántico:** La variable `mi_fuzz_fantasma` no ha sido declarada previamente mediante una asignación o como parámetro de función.

### C. Bucles de Retroalimentación Ilegales (Feedback Loops)
El lenguaje BYPASS previene explosiones de señal en el motor DSP.
* **Sintácticamente válido:** `Reverb -> Gain -> Reverb`
* **Error Semántico:** Crear un ciclo cerrado sin insertar un módulo de memoria (`Delay`) generará una falla de recursividad infinita en el procesamiento de audio.

### D. Cadenas de Ruteo Huérfanas (Missing Terminus)
Las leyes del ruteo exigen un flujo continuo desde el inicio hasta el final.
* **Sintácticamente válido:** `INPUT -> Filter -> Gain(0.5)`
* **Error Semántico:** La cadena no finaliza en `OUTPUT` ni en un `monitor`. El audio procesado en esta línea se perderá en el vacío.

### E. Propiedades Inexistentes
Ocurre en la interfaz gráfica o al acceder a miembros con notación de punto.
* **Sintácticamente válido:** `knob(target: Fuzz.volumen_magico)`
* **Error Semántico:** El módulo nativo `Fuzz` no posee una propiedad llamada `volumen_magico` (solo posee `gain` o `style`).