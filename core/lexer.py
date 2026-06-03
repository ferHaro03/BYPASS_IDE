import re
from core.errors import LexicalError

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
            'monitor':     'T_MONITOR',
            'oscilloscope':'T_OSCILLO',
            'spectrum':    'T_SPECTRUM',
            'INPUT':    'T_INPUT',
            'OUTPUT':   'T_OUTPUT'
        }

        # Módulos nativos
        self.BUILTIN_MODULES = [
            'Gain', 'Fuzz', 'Gate',           
            'Filter', 'EQ',                   
            'Delay', 'Reverb',                
            'LFO', 'Chorus',                  
            'Mixer'                           
        ]

    def tokenize(self):
        rules = [
            ('T_COMMENT',   r'#.*'),
            ('T_ARROW',     r'->'),
            ('T_NUMBER',    r'\d+(\.\d+)?(hz|ms|bpm|db|%)?'),
            ('T_STRING',    r'"[^"\n]*"'),        # Cadena cerrada correctamente
            ('T_UNCLOSED_STRING', r'"[^"\n]*'),   # CABALLO DE TROYA: Cadena sin cerrar
            ('T_ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
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
                if value in self.KEYWORDS:
                    kind = self.KEYWORDS[value]
                elif value in self.BUILTIN_MODULES:
                    kind = 'T_BUILTIN_MOD'
                elif value[0].isupper():
                    kind = 'T_USER_FUN'
                else:
                    kind = 'T_VAR_ID'
                self.tokens.append(Token(kind, value, self.line, column))
                
            elif kind == 'T_UNCLOSED_STRING':
                # Pasa directamente al Parser para ser juzgado como Error Sintáctico
                self.tokens.append(Token(kind, value, self.line, column))
                
            elif kind == 'T_MISMATCH':
                start_idx = mo.start()
                delimiters = " \t\n(),{}[];:->=+" 
                
                word_start = start_idx
                while word_start > 0 and self.source_code[word_start - 1] not in delimiters:
                    word_start -= 1
                    
                word_end = start_idx + 1
                while word_end < len(self.source_code) and self.source_code[word_end] not in delimiters:
                    word_end += 1
                    
                context_word = self.source_code[word_start:word_end]
                
                if len(context_word) > 1:
                    sug = f"Revisa la cadena completa '{context_word}'."
                else:
                    sug = "Elimina este carácter no reconocido en el lenguaje."
                    
                # TIPADO ESTRICTO: Instanciamos el objeto LexicalError
                error_obj = LexicalError(
                    line=self.line, 
                    column=column, 
                    message=f"Carácter ilegal '{value}'", 
                    suggestion=sug
                )
                self.errors.append(error_obj)
            else:
                self.tokens.append(Token(kind, value, self.line, column))
        
        self.tokens.append(Token('T_EOF', 'EOF', self.line, 1))
        return self.tokens, self.errors