from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt
import re

class BypassHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        # Keywords (Amarillo)
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#E6DB74"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        for kw in [r'\bfunction\b', r'\breturn\b', r'\bfor\b', r'\bin\b']:
            self.rules.append((re.compile(kw), keyword_fmt))

        # Módulos Dinámicos (Cian) - Cualquier palabra que empiece con Mayúscula
        module_fmt = QTextCharFormat()
        module_fmt.setForeground(QColor("#66D9EF"))
        module_fmt.setFontWeight(QFont.Weight.Bold)
        self.rules.append((re.compile(r'\b[A-Z][a-zA-Z0-9_]*\b'), module_fmt))

        # Números (Morado)
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#AE81FF"))
        self.rules.append((re.compile(r'\b\d+(\.\d+)?(hz|ms|bpm)?\b'), num_fmt))

        # Strings (Verde)
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#A6E22E"))
        self.rules.append((re.compile(r'"[^"]*"'), str_fmt))

        # Operador de Ruteo -> (Naranja)
        arrow_fmt = QTextCharFormat()
        arrow_fmt.setForeground(QColor("#FD971F"))
        arrow_fmt.setFontWeight(QFont.Weight.Bold)
        self.rules.append((re.compile(r'->'), arrow_fmt))

        # Comentarios (Gris)
        comm_fmt = QTextCharFormat()
        comm_fmt.setForeground(QColor("#75715E"))
        self.rules.append((re.compile(r'#.*'), comm_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)