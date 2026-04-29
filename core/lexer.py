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
            'for':      'T_FOR',
            'in':       'T_IN',
            'if':       'T_IF',    # Añadimos soporte futuro para lógica
            'else':     'T_ELSE',
            'INPUT':    'T_INPUT', # Puertos reservados
            'OUTPUT':   'T_OUTPUT'
        }

    def tokenize(self):
        rules = [
            ('T_COMMENT',   r'#.*'),
            ('T_ARROW',     r'->'),          # Prioridad sobre T_MINUS
            ('T_NUMBER',    r'\d+(\.\d+)?(hz|ms|bpm|db)?'), # Añadido 'db'
            ('T_STRING',    r'"[^"]*"'),
            ('T_ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('T_NEWLINE',   r'\n'),
            ('T_SKIP',      r'[ \t]+'),
            
            # Operadores Comparación
            ('T_EE',        r'=='),
            ('T_GT',        r'>'),
            ('T_LT',        r'<'),
            
            # Operadores Matemáticos y Asignación
            ('T_ASSIGN',    r'='),
            ('T_PLUS',      r'\+'),
            ('T_MINUS',     r'-'),
            ('T_MUL',       r'\*'),
            ('T_DIV',       r'/'),
            
            # Delimitadores
            ('T_COLON',     r':'),
            ('T_LPAREN',    r'\('),
            ('T_RPAREN',    r'\)'),
            ('T_LBRACE',    r'\{'),
            ('T_RBRACE',    r'\}'),
            ('T_LBRACKET',  r'\['),
            ('T_RBRACKET',  r'\]'),
            ('T_COMMA',     r','),
            ('T_DOT',       r'\.'),
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
                # Podríamos emitir un token T_NEWLINE si el parser lo requiere
                continue
            elif kind == 'T_SKIP' or kind == 'T_COMMENT':
                continue
            elif kind == 'T_ID':
                # Lógica de clasificación mejorada
                if value in self.KEYWORDS:
                    kind = self.KEYWORDS[value]
                elif value[0].isupper():
                    kind = 'T_MODULE_ID'
                else:
                    kind = 'T_VAR_ID'
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'T_MISMATCH':
                err_msg = f"Error Léxico: Carácter ilegal '{value}' en línea {self.line}, col {column}"
                self.errors.append(err_msg)
                self.tokens.append(Token('T_ERROR', value, self.line, column))
            else:
                self.tokens.append(Token(kind, value, self.line, column))
        
        return self.tokens, self.errors