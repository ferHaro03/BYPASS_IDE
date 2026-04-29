from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt
import re

class BypassHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        # 1. Módulos Generales (Cian) - LA PONEMOS PRIMERO
        # Esta regla es general, las específicas irán después para sobrescribirla
        module_fmt = QTextCharFormat()
        module_fmt.setForeground(QColor("#66D9EF"))
        module_fmt.setFontWeight(QFont.Weight.Bold)
        self.rules.append((re.compile(r'\b[A-Z][a-zA-Z0-9_]*\b'), module_fmt))

        # 2. Keywords (Amarillo)
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#E6DB74"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [r'\bfunction\b', r'\breturn\b', r'\bfor\b', r'\bin\b', r'\bif\b', r'\belse\b']
        for kw in keywords:
            self.rules.append((re.compile(kw), keyword_fmt))

        # 3. Puertos Globales (Naranja) - AL IR DESPUÉS, SOBRESCRIBE AL CIAN
        builtin_fmt = QTextCharFormat()
        builtin_fmt.setForeground(QColor("#FD971F"))
        builtin_fmt.setFontWeight(QFont.Weight.Bold)
        for bi in [r'\bINPUT\b', r'\bOUTPUT\b']:
            self.rules.append((re.compile(bi), builtin_fmt))

        # 4. Números y Unidades (Morado)
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#AE81FF"))
        self.rules.append((re.compile(r'\b\d+(\.\d+)?(hz|ms|bpm|db)?\b'), num_fmt))

        # 5. Strings (Verde)
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#A6E22E"))
        self.rules.append((re.compile(r'"[^"]*"'), str_fmt))

        # 6. Operadores (Magenta/Rojo)
        op_fmt = QTextCharFormat()
        op_fmt.setForeground(QColor("#F92672"))
        op_fmt.setFontWeight(QFont.Weight.Bold)
        operators = [r'->', r'==', r'>', r'<', r'=', r'\+', r'-', r'\*', r'/']
        for op in operators:
            self.rules.append((re.compile(op), op_fmt))

        # 7. Comentarios (Gris)
        comm_fmt = QTextCharFormat()
        comm_fmt.setForeground(QColor("#75715E"))
        self.rules.append((re.compile(comm_fmt_regex := r'#.*'), comm_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)