# 🎸 Manual de Usuario: BYPASS DSL
**Entorno de Desarrollo para Efectos de Audio**

Bienvenido a **BYPASS**, un lenguaje de dominio específico (DSL) diseñado para simplificar la creación de algoritmos de procesamiento de señal digital (DSP) mediante una sintaxis intuitiva basada en el flujo de señales.

## 📑 Contenido
- [🎸 Manual de Usuario: BYPASS DSL](#-manual-de-usuario-bypass-dsl)
  - [📑 Contenido](#-contenido)
  - [1. Interfaz del IDE](#1-interfaz-del-ide)
  - [2. Sintaxis Básica](#2-sintaxis-básica)
    - [Definición de Identificadores](#definición-de-identificadores)
    - [Tipos de Datos y Unidades](#tipos-de-datos-y-unidades)
  - [3. Módulos Nativos](#3-módulos-nativos)
  - [4. Flujo de Señal (Ruteo)](#4-flujo-de-señal-ruteo)
  - [5. Ejemplos Prácticos](#5-ejemplos-prácticos)

---

## 1. Interfaz del IDE
El IDE de BYPASS está dividido en paneles especializados para optimizar tu flujo de trabajo:

* **Explorador de Archivos (Izquierda):** Gestiona tus proyectos con extensión `.bps`.
* **Editor de Código (Centro):** Incluye resaltado de sintaxis estilo Monokai y numeración de líneas.
* **Vistas de Trabajo (Pestañas Centrales):**
    * **Source:** Donde escribes tu código.
    * **Design:** Previsualización de la interfaz de usuario (perillas, sliders).
    * **Debug:** Monitoreo en tiempo real con Osciloscopio y Analizador de Espectro.
* **Salida del Compilador (Derecha):** Inspecciona cómo el Lexer procesa tus tokens en tiempo real.

---

## 2. Sintaxis Básica

### Definición de Identificadores
* **Módulos y Funciones:** Deben comenzar con **Mayúscula** (ej. `Delay`, `MiEfecto`).
* **Variables y Parámetros:** Deben comenzar con **minúscula** (ej. `señal`, `volumen`).

### Tipos de Datos y Unidades
BYPASS entiende el contexto físico de la música. Puedes usar números con unidades integradas:
* **Frecuencia:** `440hz`
* **Tiempo:** `50ms`
* **Ganancia:** `-12db`
* **Proporción:** `50%`

---

## 3. Módulos Nativos
El lenguaje incluye "Colores Primarios" o módulos de procesamiento base:

| Categoría | Módulos Disponibles |
| :--- | :--- |
| **Dinámica** | `Gain`, `Fuzz`, `Gate` |
| **Espectro** | `Filter`, `EQ` |
| **Espacio** | `Delay`, `Reverb` |
| **Modulación** | `LFO`, `Chorus` |
| **Utilidad** | `Mixer`, `INPUT`, `OUTPUT` |

---

## 4. Flujo de Señal (Ruteo)
La magia de BYPASS reside en el operador de ruteo `->`. Este conecta la salida de un módulo con la entrada del siguiente.

**Ejemplo de cadena simple:**
```bypass
INPUT -> Fuzz(gain: 0.8) -> Gain(volume: 0.5) -> OUTPUT
```
También puedes realizar procesamiento en paralelo utilizando corchetes [ ] y enviando el resultado a un Mixer.

## 5. Ejemplos Prácticos

**Crear un Fuzz Personalizado**
```bypass
function ClassicFuzz(señal) {
    distorsion = Fuzz(gain: 0.85, style: "vintage")
    filtro = Filter(type: "BP", cutoff: 2500hz, q: 1.2)
    
    return señal -> distorsion -> filtro
}

INPUT -> ClassicFuzz -> OUTPUT
```

**Reverb Espacial (Shimmer)**
```bypass
function ShimmerReverb(entrada, brillo) {
    difusion = Filter(type: "LP", cutoff: 12000hz)
    reflexion = Delay(time: 80ms, feedback: 0.6)
    
    return entrada -> difusion -> reflexion -> Gain(brillo)
}

# Mezcla de señal limpia y procesada
[INPUT, INPUT -> ShimmerReverb(brillo: 0.75)] -> Mixer(out: "stereo") -> OUTPUT
```