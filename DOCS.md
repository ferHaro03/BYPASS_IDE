# Especificación Técnica de BYPASS

## 1. Analizador Léxico (Lexer)
El Lexer utiliza expresiones regulares para identificar las categorías léxicas del lenguaje. Actualmente soporta:

| Token | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `T_MODULE_ID` | Identificadores de módulos (Clases) | `Reverb`, `Filter` |
| `T_VAR_ID` | Identificadores de usuario | `eco`, `volumen` |
| `T_NUMBER` | Valores numéricos con unidades | `440hz`, `500ms` |
| `T_ARROW` | Operador de ruteo de audio | `->` |
| `T_ERROR` | Caracteres no reconocidos | `ñ`, `$`, `@` |

## 2. Estructura del Proyecto
- `/core`: Lógica del compilador (Lexer, Parser).
- `/ui`: Interfaz gráfica y componentes visuales.
- `/assets`: Recursos de estilo y branding.