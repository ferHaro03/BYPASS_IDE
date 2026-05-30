import difflib

# ==========================================
# 🌳 NODOS DEL ÁRBOL DE SINTAXIS ABSTRACTA
# ==========================================

class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return "\n".join([str(stmt) for stmt in self.statements])

class AudioRouteNode(ASTNode):
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op_token.value} {self.right})"

class SplitterNode(ASTNode):
    def __init__(self, branches):
        self.branches = branches 
    def __repr__(self):
        branches_str = ", ".join([str(b) for b in self.branches])
        return f"Splitter[{branches_str}]"

class ModuleCallNode(ASTNode):
    def __init__(self, token, params):
        self.token = token
        self.params = params
    def __repr__(self):
        params_str = ", ".join([f"{k}:{v}" for k, v in self.params])
        return f"{self.token.value}({params_str})"

class AtomicNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    def __repr__(self):
        return f"{self.token.value}"
    
class FunctionDeclNode(ASTNode):
    def __init__(self, name_token, params, body):
        self.name_token = name_token
        self.params = params
        self.body = body
    def __repr__(self):
        cuerpo_str = "\n  ".join([str(stmt) for stmt in self.body])
        return f"FunctionDef({self.name_token.value}, args={self.params}) {{\n  {cuerpo_str}\n}}"

class AssignmentNode(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value
    def __repr__(self):
        return f"Assign({self.target} = {self.value})"

class ReturnNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class UILayoutNode(ASTNode):
    def __init__(self, widgets):
        self.widgets = widgets
    def __repr__(self):
        w_str = "\n  ".join([str(w) for w in self.widgets])
        return f"UILayout {{\n  {w_str}\n}}"

class ConditionNode(ASTNode):
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right
    def __repr__(self):
        return f"{self.left} {self.op_token.value} {self.right}"

class IfNode(ASTNode):
    def __init__(self, condition, true_body, false_body=None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body
    def __repr__(self):
        t_str = "\n  ".join([str(s) for s in self.true_body])
        res = f"If({self.condition}) {{\n  {t_str}\n}}"
        if self.false_body:
            f_str = "\n  ".join([str(s) for s in self.false_body])
            res += f" Else {{\n  {f_str}\n}}"
        return res


# ==========================================
# ⚙️ ANALIZADOR SINTÁCTICO (PARSER)
# ==========================================

class ParserBYPASS:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.kind != 'T_SKIP' and t.kind != 'T_COMMENT' and t.kind != 'T_NEWLINE']
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # --- RECUPERACIÓN INTELIGENTE DE ERRORES ---
    def report_error(self, message, suggestion):
        """Registra el error con contexto y sugerencia sin detener el IDE"""
        linea = self.current_token.line if self.current_token else "EOF"
        token_val = self.current_token.value if self.current_token else "Fin de archivo"
        error_completo = f"❌ Línea {linea} | Error cerca de '{token_val}': {message}\n   💡 Sugerencia: {suggestion}"
        self.errors.append(error_completo)

    def synchronize(self):
        """Avanza hasta un punto seguro para seguir leyendo si el error es grave"""
        self.advance()
        while self.current_token and self.current_token.kind != 'T_EOF':
            if self.current_token.kind in ['T_FUNCTION', 'T_IF', 'T_LAYOUT', 'T_INPUT', 'T_VAR_ID']:
                return
            self.advance()

    class DummyToken:
        """Token falso para que el AST no explote si falta una variable o símbolo"""
        def __init__(self, value="ERROR"):
            self.value = value
            self.kind = "T_ERROR"

    def eat(self, token_kind, suggestion="Revisa la sintaxis de BYPASS."):
        """Consume el token si coincide, si no, reporta inteligentemente y salva el AST"""
        if self.current_token and self.current_token.kind == token_kind:
            token = self.current_token
            self.advance()
            return token
        else:
            kind_actual = self.current_token.kind if self.current_token else "EOF"
            self.report_error(f"Se esperaba {token_kind} pero se encontró {kind_actual}", suggestion)
            return self.DummyToken()

    # --- MÉTODOS DE LECTURA GRAMATICAL ---
    def parse_module_call(self, module_token):
        self.eat('T_LPAREN', "Los módulos deben llevar paréntesis, ej: Filter(cutoff: 500hz)")
        params = []
        while self.current_token and self.current_token.kind != 'T_RPAREN' and self.current_token.kind != 'T_EOF':
            
            param_name = "desconocido"
            if self.current_token.kind in ['T_VAR_ID', 'T_LABEL']:
                param_name = self.current_token.value
                self.advance()
            else:
                self.report_error("Falta nombre de parámetro.", f"Usa el formato 'nombre_parametro: {self.current_token.value}'")
                self.advance()
            
            self.eat('T_COLON', "Separa el parámetro de su valor con dos puntos ':'")

            if self.current_token and self.current_token.kind in ['T_NUMBER', 'T_STRING', 'T_VAR_ID', 'T_BUILTIN_MOD', 'T_USER_FUN']:
                param_value = self.current_token.value
                self.advance()
                
                if self.current_token and self.current_token.kind == 'T_DOT':
                    self.eat('T_DOT')
                    if self.current_token.kind == 'T_VAR_ID':
                        prop = self.current_token.value
                        param_value = f"{param_value}.{prop}"
                        self.advance()
                params.append((param_name, param_value))
            else:
                self.report_error("Valor inválido.", "Usa números, variables o strings.")
                self.advance()
                
            if self.current_token and self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
            elif self.current_token and self.current_token.kind != 'T_RPAREN':
                 self.report_error("Falta coma.", "Separa múltiples parámetros con comas ','")
                 self.advance()
                
        self.eat('T_RPAREN', "Cierra los parámetros con ')'")
        return ModuleCallNode(module_token, params)

    def parse_atom(self):
        token = self.current_token
        if not token: return AtomicNode(self.DummyToken("None"))
        
        # 1. ¿Es un Splitter?
        if token.kind == 'T_LBRACKET':
            self.eat('T_LBRACKET')
            branches = []
            branches.append(self.parse_routing())
            while self.current_token and self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
                branches.append(self.parse_routing())
            self.eat('T_RBRACKET', "Cierra el arreglo paralelo con ']'")
            return SplitterNode(branches)

        # 2. Validar Atomo
        valid_atoms = ['T_INPUT', 'T_OUTPUT', 'T_BUILTIN_MOD', 'T_USER_FUN', 'T_VAR_ID', 'T_MONITOR', 'T_STRING', 'T_NUMBER']
        
        if token.kind in valid_atoms:
            # 💡 PREDICCIÓN ESTRUCTURAL DE PUERTOS (INPU / OUTPU)
            # Solución aplicada: ahora buscamos en T_VAR_ID y T_USER_FUN
            if token.kind in ['T_VAR_ID', 'T_USER_FUN']:
                matches = difflib.get_close_matches(token.value.upper(), ['INPUT', 'OUTPUT'], n=1, cutoff=0.75)
                if matches:
                    puerto = matches[0]
                    self.report_error(f"Puerto sospechoso '{token.value}'.", f"¿Quisiste escribir '{puerto}'?")
                    # Magia: Corregimos el token en la memoria y lo dejamos pasar
                    token.kind = f'T_{puerto}'
                    token.value = puerto
            
            self.advance()
            if self.current_token and self.current_token.kind == 'T_LPAREN':
                return self.parse_module_call(token)
            return AtomicNode(token)
        
        self.report_error("Elemento de audio irreconocible.", "Usa INPUT, OUTPUT, Módulos o Variables.")
        self.advance()
        return AtomicNode(self.DummyToken(token.value))

    def parse_routing(self):
        left = self.parse_atom()
        if self.current_token and self.current_token.kind == 'T_ARROW':
            op = self.current_token
            self.advance()
            right = self.parse_routing()
            return AudioRouteNode(left, op, right)
        return left

    def parse_function_decl(self):
        self.eat('T_FUNCTION')
        name_token = self.eat('T_USER_FUN', "La función debe iniciar con Mayúscula.")
        self.eat('T_LPAREN', "Faltan paréntesis '(' para los parámetros.")
        
        params = []
        if self.current_token and self.current_token.kind == 'T_VAR_ID':
            params.append(self.eat('T_VAR_ID').value)
            while self.current_token and self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
                params.append(self.eat('T_VAR_ID').value)
                
        self.eat('T_RPAREN', "Cierra los parámetros con ')'")
        self.eat('T_LBRACE', "Abre el cuerpo de la función con '{'")
        
        body_statements = []
        while self.current_token and self.current_token.kind != 'T_RBRACE' and self.current_token.kind != 'T_EOF':
            body_statements.append(self.parse_statement())
            
        self.eat('T_RBRACE', "Cierra el cuerpo de la función con '}'")
        return FunctionDeclNode(name_token, params, body_statements)

    def parse_ui_layout(self):
        self.eat('T_LAYOUT')
        self.eat('T_LBRACE', "Abre el bloque de UI con '{'")
        widgets = []
        
        ui_tokens = ['T_KNOB', 'T_SWITCH', 'T_SLIDER', 'T_LABEL']
        while self.current_token and self.current_token.kind != 'T_RBRACE' and self.current_token.kind != 'T_EOF':
            if self.current_token.kind in ui_tokens:
                widget_token = self.current_token
                self.advance()
                widgets.append(self.parse_module_call(widget_token))
            else:
                self.report_error("Elemento UI inválido.", "Usa knob, switch, slider o label.")
                self.advance()
                
        self.eat('T_RBRACE', "Cierra el bloque de UI con '}'")
        return UILayoutNode(widgets)

    def parse_if_statement(self):
        self.eat('T_IF')
        self.eat('T_LPAREN', "La condición debe ir entre paréntesis '()'")
        
        left = self.parse_atom()
        op_tokens = ['T_EE', 'T_GE', 'T_LE', 'T_NE', 'T_GT', 'T_LT']
        if self.current_token and self.current_token.kind in op_tokens:
            op = self.current_token
            self.advance()
            right = self.parse_atom()
            condition = ConditionNode(left, op, right)
        else:
            self.report_error("Falta operador lógico.", "Usa ==, !=, >=, <=, >, <")
            condition = ConditionNode(left, self.DummyToken("=="), self.DummyToken("error"))
            self.advance()
            
        self.eat('T_RPAREN', "Cierra la condición con ')'")
        self.eat('T_LBRACE', "Abre el bloque If con '{'")
        
        true_body = []
        while self.current_token and self.current_token.kind != 'T_RBRACE' and self.current_token.kind != 'T_EOF':
            true_body.append(self.parse_statement())
        self.eat('T_RBRACE', "Cierra el bloque If con '}'")
        
        false_body = None
        if self.current_token and self.current_token.kind == 'T_ELSE':
            self.eat('T_ELSE')
            self.eat('T_LBRACE', "Abre el bloque Else con '{'")
            false_body = []
            while self.current_token and self.current_token.kind != 'T_RBRACE' and self.current_token.kind != 'T_EOF':
                false_body.append(self.parse_statement())
            self.eat('T_RBRACE', "Cierra el bloque Else con '}'")
            
        return IfNode(condition, true_body, false_body)

    def parse_statement(self):
        token = self.current_token
        if not token: return None
        
        try:
            # 💡 PREDICCIÓN ESTRUCTURAL LL(1) PARA PALABRAS CLAVE
            # Solución aplicada: ahora buscamos en T_VAR_ID y T_USER_FUN
            if token.kind in ['T_VAR_ID', 'T_USER_FUN']:
                # Miramos al futuro (lookahead)
                next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                
                # Si una supuesta "variable" va seguida de otra variable, un paréntesis o una llave 
                # (ej: `retur entrada`, `fuction MiEfecto(...)`, `u_layout {`), es un claro error tipográfico
                if next_token and next_token.kind in ['T_VAR_ID', 'T_USER_FUN', 'T_LPAREN', 'T_LBRACE']:
                    keywords = {'return': 'T_RETURN', 'function': 'T_FUNCTION', 'ui_layout': 'T_LAYOUT', 'if': 'T_IF', 'else': 'T_ELSE'}
                    matches = difflib.get_close_matches(token.value, keywords.keys(), n=1, cutoff=0.7)
                    if matches:
                        keyword = matches[0]
                        self.report_error(f"Comando irreconocible '{token.value}'.", f"Por la estructura, ¿quisiste escribir '{keyword}'?")
                        
                        # Magia: Mutamos el token en tiempo real para salvar el AST
                        token.kind = keywords[keyword]
                        token.value = keyword
            
            # Ahora dejamos que el flujo normal se encargue (¡con el token ya arreglado!)
            if token.kind == 'T_FUNCTION': return self.parse_function_decl()
            if token.kind == 'T_LAYOUT': return self.parse_ui_layout()
            if token.kind == 'T_IF': return self.parse_if_statement()
            if token.kind == 'T_RETURN':
                self.eat('T_RETURN')
                return ReturnNode(self.parse_routing())
                
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            # Si es una asignación
            if token.kind == 'T_VAR_ID' and next_token and next_token.kind == 'T_ASSIGN':
                target_name = self.current_token.value
                self.advance()
                self.advance() # consume T_ASSIGN '='
                value = self.parse_routing()
                return AssignmentNode(target_name, value)
                
            # Si no es palabra clave ni asignación, DEBE ser una ruta válida (ej: INPU -> OUTPUT)
            return self.parse_routing()
            
        except Exception as e:
            self.errors.append(str(e))
            self.synchronize()
            return None

    def parse(self):
        """Punto de entrada principal para el análisis sintáctico"""
        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].kind == 'T_EOF'):
            return "Código vacío"
        
        statements = []
        while self.current_token and self.current_token.kind != 'T_EOF':
            stmt = self.parse_statement()
            if stmt: statements.append(stmt)
                
        return ProgramNode(statements)