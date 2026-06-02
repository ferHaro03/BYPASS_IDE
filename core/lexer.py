import re

class Token:
    def __init__(self, kind, value, line, column):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.kind:<15} | {self.value}"

class LexerBYPASS:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.errors = []
        self.line = 1
        self.line_start = 0
        
        # Diccionario de Palabras Reservadas
        self.KEYWORDS = {
            'function': 'T_FUNCTION',
            'return':   'T_RETURN',
            'if':       'T_IF',
            'else':     'T_ELSE',
            'for':      'T_FOR',
            'in':       'T_IN',
            'ui_layout':'T_LAYOUT',
            'knob':     'T_KNOB',
            'switch':   'T_SWITCH',
            'slider':   'T_SLIDER',
            'label':    'T_LABEL',
            # Tokens de Diagnóstico (Solo para el IDE)
            'monitor':     'T_MONITOR',
            'oscilloscope':'T_OSCILLO',
            'spectrum':    'T_SPECTRUM',
            'INPUT':    'T_INPUT',
            'OUTPUT':   'T_OUTPUT'
        }

        # Módulos nativos (Colores Primarios)
        self.BUILTIN_MODULES = [
            'Gain', 'Fuzz', 'Gate',           # Dinámica
            'Filter', 'EQ',                   # Espectro
            'Delay', 'Reverb',                # Espacio
            'LFO', 'Chorus',                  # Modulación
            'Mixer'                           # Utilidad
        ]

    def tokenize(self):
        rules = [
            ('T_COMMENT',   r'#.*'),
            ('T_ARROW',     r'->'),
            ('T_NUMBER',    r'\d+(\.\d+)?(hz|ms|bpm|db|%)?'),
            ('T_STRING',    r'"[^"]*"'),
            ('T_ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'), # Captura cualquier palabra
            ('T_NEWLINE',   r'\n'),
            ('T_SKIP',      r'[ \t]+'),
            ('T_EE',        r'=='),
            ('T_GE',        r'>='),
            ('T_LE',        r'<='),
            ('T_NE',        r'!='),
            ('T_ASSIGN',    r'='),
            ('T_GT',        r'>'),
            ('T_LT',        r'<'),
            ('T_PLUS',      r'\+'),
            ('T_MINUS',     r'-'),
            ('T_MUL',       r'\*'),
            ('T_DIV',       r'/'),
            ('T_COLON',     r':'),
            ('T_SEMICOLON', r';'),
            ('T_COMMA',     r','),
            ('T_DOT',       r'\.'),
            ('T_LPAREN',    r'\('),
            ('T_RPAREN',    r'\)'),
            ('T_LBRACE',    r'\{'),
            ('T_RBRACE',    r'\}'),
            ('T_LBRACKET',  r'\['),
            ('T_RBRACKET',  r'\]'),
            ('T_MISMATCH',  r'.'), 
        ]
        
        regex = '|'.join('(?P<%s>%s)' % pair for pair in rules)
        
        for mo in re.finditer(regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - self.line_start + 1
            
            if kind == 'T_NEWLINE':
                self.line_start = mo.end()
                self.line += 1
                continue
            elif kind == 'T_SKIP' or kind == 'T_COMMENT':
                continue
            elif kind == 'T_ID':
                # --- LÓGICA DE CLASIFICACIÓN REFINADA ---
                if value in self.KEYWORDS:
                    kind = self.KEYWORDS[value]
                elif value in self.BUILTIN_MODULES:
                    kind = 'T_BUILTIN_MOD'
                elif value[0].isupper():
                    kind = 'T_USER_FUN'
                else:
                    kind = 'T_VAR_ID'
                self.tokens.append(Token(kind, value, self.line, column))
                
            elif kind == 'T_MISMATCH':
                # --- NUEVA LÓGICA: Extracción Inteligente de Contexto ---
                start_idx = mo.start()
                # Delimitadores que cortan una palabra en tu lenguaje
                delimiters = " \t\n(),{}[];:->=+" 
                
                # 1. Retroceder para encontrar el inicio de la palabra rota
                word_start = start_idx
                while word_start > 0 and self.source_code[word_start - 1] not in delimiters:
                    word_start -= 1
                    
                # 2. Avanzar para encontrar el final de la palabra rota
                word_end = start_idx + 1
                while word_end < len(self.source_code) and self.source_code[word_end] not in delimiters:
                    word_end += 1
                    
                # 3. Extraer la cadena completa
                context_word = self.source_code[word_start:word_end]
                
                # 4. Construir el mensaje de error condicional
                err_msg = f"❌ Error Léxico: Carácter ilegal '{value}' en línea {self.line}, col {column}."
                
                # Si la longitud es mayor a 1, significa que no estaba aislado
                if len(context_word) > 1:
                    err_msg += f"\n   💡 Sugerencia: Revisa la cadena completa '{context_word}'."
                    
                self.errors.append(err_msg)
                
                # Mantenemos el "Camino A" purificando la entrada (no se añade a self.tokens)
                # ---------------------------------------------------------
            else:
                self.tokens.append(Token(kind, value, self.line, column))
        
        self.tokens.append(Token('T_EOF', 'EOF', self.line, 1))
        return self.tokens, self.errors