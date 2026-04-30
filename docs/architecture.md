# Arquitectura del Proyecto: BYPASS IDE

## 1. Visión General
BYPASS es un entorno de desarrollo integrado (IDE) especializado en la creación de efectos de audio. La arquitectura sigue un modelo modular que separa la interfaz de usuario (UI) de la lógica del compilador (Core).

## 2. Estructura de Directorios Sugerida
```text
BYPASS_PROJECT/
├── main.py              # Punto de entrada de la aplicación
├── core/                # Corazón del compilador
│   ├── lexer.py         # Analizador léxico
│   └── parser.py        # Analizador sintáctico
├── ui/                  # Interfaz gráfica (PyQt6)
│   ├── main_window.py   # Ventana principal
│   └── highlighter.py   # Resaltado de sintaxis
├── docs/                # Documentación técnica del proyecto
│   ├── lexical_analysis.md
│   └── architecture.md
└── README.md            # Documentación principal del repositorio
```

## 3. Componentes del IDE
* **Source View:** Editor con resaltado de sintaxis en tiempo real.
* **Design View:** Previsualización de la interfaz del plugin (RAD).
* **Debug View:** Monitoreo de señales (Osciloscopio y Spectrum).
* **Compiler Output:** Paneles de Lexer, AST y Tabla de Símbolos.