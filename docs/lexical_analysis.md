# Especificación del Análisis Léxico: Lenguaje BYPASS

## 1. Introducción
El análisis léxico es la primera fase del compilador de BYPASS. Su función es transformar el flujo de caracteres del código fuente en una secuencia de **Tokens**. A diferencia de los lenguajes de propósito general, BYPASS clasifica los símbolos no solo por su forma sintáctica, sino por su relevancia en el dominio del procesamiento de señales digitales (DSP) y el diseño de interfaces de audio.

## 2. Tabla Maestra de Tokens (v4.0)

| Categoría | Token | Lexema de Ejemplo | Descripción y Uso |
| :--- | :--- | :--- | :--- |
| **Flujo Global** | `T_INPUT` / `T_OUTPUT` | `INPUT`, `OUTPUT` | Puntos de entrada y salida de audio del sistema (Tarjeta de sonido/DAW). |
| **Módulos Nativos** | `T_BUILTIN_MOD` | `Filter`, `Delay`, `Fuzz` | Procesadores de audio base ("Colores Primarios") integrados en el motor. |
| **Usuario** | `T_USER_FUN` | `Shimmer`, `MiEfecto` | Algoritmos definidos por el usuario (Identificadores con inicial Mayúscula). |
| **Variables** | `T_VAR_ID` | `difusion`, `volumen` | Identificadores para instancias de módulos o valores locales (Minúsculas). |
| **Estructura** | `T_FUNCTION`, `T_RETURN` | `function`, `return` | Palabras clave para la definición de bloques lógicos. |
| **Datos de Audio** | `T_NUMBER` | `440hz`, `-12db`, `50ms` | Valores numéricos que incluyen magnitudes físicas de audio. |
| **Conexión** | `T_ARROW` | `->` | Operador de ruteo que define el flujo de señal entre nodos. |
| **Interfaz (GUI)** | `T_LAYOUT`, `T_KNOB` | `ui_layout`, `knob` | Declaración de componentes visuales y controles para el plugin final. |
| **Diagnóstico** | `T_MONITOR` | `monitor`, `oscilloscope` | Herramientas de inspección exclusivas del IDE de desarrollo. |
| **Lógica** | `T_EE`, `T_GE`, `T_NE` | `==`, `>=`, `!=` | Operadores de comparación para estructuras de control de flujo. |
| **Agrupación** | `T_LBRACKET`, `T_LBRACE` | `[ ]`, `{ }` | Delimitadores para procesamiento paralelo y bloques de código. |

## 3. Tipos de Datos de Dominio
En BYPASS, los tokens de datos se categorizan para facilitar el posterior análisis semántico:
* **Escalares y Magnitudes:** El token `T_NUMBER` soporta unidades específicas (`hz`, `ms`, `db`, `%`). Esto permite que el compilador valide si un valor es apto para un parámetro (ej. un `cutoff` no puede recibir `ms`).
* **Objetos Procesadores:** Los tokens `T_BUILTIN_MOD` y `T_USER_FUN` representan nodos de procesamiento que pueden recibir y entregar flujos de audio.

## 4. Gestión de Errores Léxicos
Un error léxico en BYPASS ocurre cuando el analizador encuentra una secuencia de caracteres que no pertenece al alfabeto definido del lenguaje.

### Casos Comunes de Error:
1. **Caracteres Ilegales:** Uso de símbolos no definidos en las reglas de expresiones regulares, como `@`, `$`, `?` o `¿`.
2. **Malformación de Unidades:** El Lexer espera unidades de audio específicas. Una unidad no reconocida dejará caracteres "huérfanos".
3. **Strings Incompletos:** Cadenas de texto que no cierran sus comillas antes del final de la línea.
4. **Identificadores Inválidos:** Nombres que intentan comenzar con caracteres numéricos.