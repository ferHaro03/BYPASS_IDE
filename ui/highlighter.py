from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt
import re

class BypassHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        # --- 1. IDENTIFICADORES DE USUARIO (Nivel Base) ---
        user_fun_fmt = QTextCharFormat()
        user_fun_fmt.setForeground(QColor("#A6E22E")) 
        user_fun_fmt.setFontItalic(True)
        self.rules.append((re.compile(r'\b[A-Z][a-zA-Z0-9_]*\b'), user_fun_fmt))

        # --- 2. MÓDULOS NATIVOS / COLORES PRIMARIOS (Prioridad Media) ---
        builtin_mod_fmt = QTextCharFormat()
        builtin_mod_fmt.setForeground(QColor("#66D9EF")) 
        builtin_mod_fmt.setFontWeight(QFont.Weight.Bold)
        builtin_mod_fmt.setFontItalic(False) 
        nativos = r'\b(Gain|Fuzz|Gate|Filter|EQ|Delay|Reverb|LFO|Chorus|Mixer)\b'
        self.rules.append((re.compile(nativos), builtin_mod_fmt))

        # --- 3. PUERTOS GLOBALES (Prioridad Máxima) ---
        builtin_fmt = QTextCharFormat()
        builtin_fmt.setForeground(QColor("#FD971F")) 
        builtin_fmt.setFontWeight(QFont.Weight.Bold)
        for bi in [r'\bINPUT\b', r'\bOUTPUT\b']:
            self.rules.append((re.compile(bi), builtin_fmt))

        # --- 4. HERRAMIENTAS DE DIAGNÓSTICO (NUEVO - Color Técnico) ---
        # monitor, oscilloscope, spectrum
        diag_fmt = QTextCharFormat()
        diag_fmt.setForeground(QColor("#98AFC7")) # Color Slate/Acero
        diag_fmt.setFontWeight(QFont.Weight.Bold)
        diagnostics = [r'\bmonitor\b', r'\boscilloscope\b', r'\bspectrum\b']
        for diag in diagnostics:
            self.rules.append((re.compile(diag), diag_fmt))

        # --- 5. KEYWORDS ESTRUCTURALES (Amarillo) ---
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#E6DB74"))
        kw_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            r'\bfunction\b', r'\breturn\b', r'\bif\b', r'\belse\b', 
            r'\bfor\b', r'\bin\b', r'\bui_layout\b', r'\btest_source\b'
        ]
        for kw in keywords:
            self.rules.append((re.compile(kw), kw_fmt))

        # --- 6. GUI WIDGETS (Naranja claro) ---
        gui_fmt = QTextCharFormat()
        gui_fmt.setForeground(QColor("#FFB86C"))
        gui_widgets = [r'\bknob\b', r'\bswitch\b', r'\bslider\b', r'\blabel\b']
        for widget in gui_widgets:
            self.rules.append((re.compile(widget), gui_fmt))

        # --- 7. NÚMEROS Y UNIDADES (Morado) ---
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#AE81FF"))
        self.rules.append((re.compile(r'\b\d+(\.\d+)?(hz|ms|bpm|db|%)?\b'), num_fmt))

        # --- 8. OPERADORES Y RUTEO (Magenta) ---
        op_fmt = QTextCharFormat()
        op_fmt.setForeground(QColor("#F92672"))
        op_fmt.setFontWeight(QFont.Weight.Bold)
        operators = [r'->', r'==', r'>=', r'<=', r'!=', r'>', r'<', r'=', r'\+', r'-', r'\*', r'/']
        for op in operators:
            self.rules.append((re.compile(op), op_fmt))

        # --- 9. STRINGS (Verde crema) ---
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#E6DB74"))
        self.rules.append((re.compile(r'"[^"]*"'), str_fmt))

        # --- 10. COMENTARIOS (Gris) ---
        comm_fmt = QTextCharFormat()
        comm_fmt.setForeground(QColor("#75715E"))
        self.rules.append((re.compile(r'#.*'), comm_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)