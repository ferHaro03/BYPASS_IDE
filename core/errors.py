# ==========================================
# 🚨 SISTEMA DE TIPADO DE ERRORES (BYPASS)
# ==========================================

class BypassError(Exception):
    """Clase base estricta para todos los errores de compilación."""
    def __init__(self, line, column, message, suggestion):
        self.line = line
        self.column = column
        self.message = message
        self.suggestion = suggestion

class LexicalError(BypassError):
    """Errores de vocabulario: caracteres ilegales, léxico roto."""
    def __str__(self):
        return f"❌ [ERROR LÉXICO] Línea {self.line}, Col {self.column} | {self.message}\n   💡 Sugerencia: {self.suggestion}"

class SyntaxError(BypassError):
    """Errores de estructura: comillas faltantes, llaves desbalanceadas, reglas de producción."""
    def __str__(self):
        return f"❌ [ERROR SINTÁCTICO] Línea {self.line} | {self.message}\n   💡 Sugerencia: {self.suggestion}"

class SemanticError(BypassError):
    """Errores de contexto: tipos incompatibles, variables no declaradas."""
    def __str__(self):
        return f"❌ [ERROR SEMÁNTICO] Línea {self.line} | {self.message}\n   💡 Sugerencia: {self.suggestion}"