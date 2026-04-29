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
        self.errors = [] # Nueva lista para recolectar errores sin detenerse
        self.line = 1
        self.line_start = 0
        self.KEYWORDS = ['function', 'return', 'for', 'in']

    def tokenize(self):
        rules = [
            ('T_COMMENT',   r'#.*'),                   
            ('T_ARROW',     r'->'),                    
            ('T_NUMBER',    r'\d+(\.\d+)?(hz|ms|bpm)?'),
            ('T_STRING',    r'"[^"]*"'),               
            ('T_ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'), # Sin la ñ
            ('T_NEWLINE',   r'\n'),                    
            ('T_SKIP',      r'[ \t]+'),                
            ('T_ASSIGN',    r'='),
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
            elif kind == 'T_SKIP' or kind == 'T_COMMENT':
                continue
            elif kind == 'T_ID':
                if value in self.KEYWORDS:
                    kind = f'T_{value.upper()}'
                elif value[0].isupper():
                    kind = 'T_MODULE_ID'
                else:
                    kind = 'T_VAR_ID'
                self.tokens.append(Token(kind, value, self.line, column))
            elif kind == 'T_MISMATCH':
                # En lugar de raise, guardamos el error y seguimos
                err_msg = f"Error Léxico: Carácter ilegal '{value}' en línea {self.line}, col {column}"
                self.errors.append(err_msg)
                self.tokens.append(Token('T_ERROR', value, self.line, column))
            else:
                self.tokens.append(Token(kind, value, self.line, column))
        
        return self.tokens, self.errors