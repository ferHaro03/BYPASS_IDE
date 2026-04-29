# BYPASS IDE 🎸🔊
**Un lenguaje de dominio específico (DSL) para el diseño de efectos de audio.**

BYPASS es un entorno de desarrollo integrado diseñado para que músicos y productores puedan programar sus propios algoritmos de procesamiento de señal (DSP) de forma intuitiva.

## ✨ Características actuales
- **Lexer Resiliente:** Identificación de tokens en tiempo real con manejo de errores no bloqueante.
- **Editor Pro:** Numeración de líneas, resaltado de sintaxis (Monokai style) y soporte para caracteres latinos.
- **Explorador de Archivos:** Gestión de proyectos `.bps` integrada.
- **Interfaz Moderna:** Construida en Python con PyQt6, optimizada para flujo de trabajo de ingeniería.

## 🛠️ Requisitos
- Python 3.10+
- PyQt6

## 🚀 Instalación y Uso
1. Clona el repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/BYPASS_IDE.git](https://github.com/tu-usuario/BYPASS_IDE.git)

2. Instala las dependencias:
   ```bash
   pip install PyQt6

3. Ejecuta el IDE:
   ```bash
   python main.py

## 📖 Gramática del Lenguaje (Avance)
BYPASS utiliza una sintaxis basada en el flujo de señal:

- **Módulos:** Empiezan con Mayúscula (Delay, Fuzz).
- **Variables:** Empiezan con minúscula (señal, mezcla).
- **Ruteo:** Operador -> para conectar módulos.

