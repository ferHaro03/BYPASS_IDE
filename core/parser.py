class ASTNode:
    """Clase base para todos los nodos del Árbol de Sintaxis Abstracta"""
    pass

class AudioRouteNode(ASTNode):
    """Representa una conexión binaria: origen -> destino"""
    def __init__(self, left, op_token, right):
        self.left = left       # Nodo a la izquierda (origen)
        self.op_token = op_token # El token T_ARROW (->)
        self.right = right     # Nodo a la derecha (destino)

    def __repr__(self):
        return f"({self.left} {self.op_token.value} {self.right})"

class AtomicNode(ASTNode):
    """Representa un componente individual (INPUT, Filter, Gain, etc.)"""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"{self.token.value}"

class ParserBYPASS:
    def __init__(self, tokens):
        """
        Inicializa el Parser con la lista de tokens generada por el Lexer.
        """
        self.tokens = tokens
        self.pos = 0
        # Filtramos tokens de salto o comentarios si el lexer no lo hizo
        self.tokens = [t for t in tokens if t.kind != 'T_SKIP']
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        """Avanza al siguiente token en la lista"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def eat(self, token_kind):
        """
        Compara el token actual con el tipo esperado. 
        Si coincide, lo consume y avanza; si no, lanza un error.
        """
        if self.current_token and self.current_token.kind == token_kind:
            token = self.current_token
            self.advance()
            return token
        else:
            kind_actual = self.current_token.kind if self.current_token else "EOF"
            linea = self.current_token.line if self.current_token else "desconocida"
            raise Exception(f"Error Sintáctico: Se esperaba {token_kind} pero se encontró {kind_actual} en línea {linea}")

    def parse_atom(self):
        """
        Procesa un componente atómico. 
        En BYPASS, un ruteo comienza con un identificador o palabra reservada de puerto.
        """
        token = self.current_token
        valid_atoms = [
            'T_INPUT', 'T_OUTPUT', 'T_BUILTIN_MOD', 
            'T_USER_FUN', 'T_VAR_ID', 'T_MONITOR'
        ]
        
        if token and token.kind in valid_atoms:
            self.advance()
            return AtomicNode(token)
        
        raise Exception(f"Error Sintáctico: Componente de audio inválido '{token.value}' en línea {token.line}")

    def parse_routing(self):
        """
        Implementa la gramática: routing -> atom (ARROW routing | epsilon)
        Esta estructura recursiva permite cadenas como: A -> B -> C -> D
        """
        left = self.parse_atom()

        # Si el siguiente token es una flecha, estamos ante una conexión
        if self.current_token and self.current_token.kind == 'T_ARROW':
            op = self.eat('T_ARROW')
            right = self.parse_routing() # Llamada recursiva para el resto de la cadena
            return AudioRouteNode(left, op, right)
            
        return left

    def parse(self):
        """
        Punto de entrada principal para el análisis sintáctico.
        """
        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].kind == 'T_EOF'):
            return "Código vacío"

        try:
            # Iniciamos el análisis desde la regla de ruteo
            result = self.parse_routing()
            
            # Al terminar, deberíamos estar en el final del archivo (T_EOF)
            if self.current_token and self.current_token.kind != 'T_EOF':
                raise Exception(f"Error: Contenido extra inesperado después de la sentencia en línea {self.current_token.line}")
                
            return result
        except Exception as e:
            return f"Error en el Parser: {str(e)}"