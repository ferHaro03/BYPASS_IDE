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

# --- NUEVOS NODOS AST PARA LA ENTREGA FINAL ---
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
# ----------------------------------------------

class ParserBYPASS:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.kind != 'T_SKIP' and t.kind != 'T_COMMENT' and t.kind != 'T_NEWLINE']
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = [] # <-- NUEVO: Lista para recolectar errores sintácticos

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_kind):
        if self.current_token and self.current_token.kind == token_kind:
            token = self.current_token
            self.advance()
            return token
        else:
            kind_actual = self.current_token.kind if self.current_token else "EOF"
            linea = self.current_token.line if self.current_token else "desconocida"
            raise Exception(f"Error Sintáctico: Se esperaba {token_kind} pero se encontró {kind_actual} en línea {linea}")

    def synchronize(self):
        """
        NUEVO: Recuperación en Modo Pánico.
        Avanza descartando tokens hasta encontrar uno que pueda iniciar una nueva sentencia segura.
        """
        self.advance()
        while self.current_token and self.current_token.kind != 'T_EOF':
            # Puntos seguros donde el Parser sabe cómo volver a empezar
            if self.current_token.kind in ['T_FUNCTION', 'T_IF', 'T_LAYOUT', 'T_INPUT', 'T_VAR_ID']:
                return
            self.advance()

    def parse_module_call(self, module_token):
        self.eat('T_LPAREN')
        params = []
        while self.current_token and self.current_token.kind != 'T_RPAREN':
            param_name = self.eat('T_VAR_ID').value 
            self.eat('T_COLON') 
            
            if self.current_token.kind in ['T_NUMBER', 'T_STRING', 'T_VAR_ID', 'T_BUILTIN_MOD', 'T_USER_FUN']:
                param_value = self.current_token.value
                self.advance()
                if self.current_token and self.current_token.kind == 'T_DOT':
                    self.eat('T_DOT')
                    prop = self.eat('T_VAR_ID').value
                    param_value = f"{param_value}.{prop}"
                params.append((param_name, param_value))
            else:
                raise Exception(f"Valor de parámetro inválido en línea {self.current_token.line}")
                
            if self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
                
        self.eat('T_RPAREN')
        return ModuleCallNode(module_token, params)

    def parse_atom(self):
        token = self.current_token
        
        if token and token.kind == 'T_LBRACKET':
            self.eat('T_LBRACKET')
            branches = []
            branches.append(self.parse_routing())
            while self.current_token and self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
                branches.append(self.parse_routing())
            self.eat('T_RBRACKET')
            return SplitterNode(branches)

        valid_atoms = ['T_INPUT', 'T_OUTPUT', 'T_BUILTIN_MOD', 'T_USER_FUN', 'T_VAR_ID', 'T_MONITOR', 'T_STRING', 'T_NUMBER']
        
        if token and token.kind in valid_atoms:
            self.advance()
            if self.current_token and self.current_token.kind == 'T_LPAREN':
                return self.parse_module_call(token)
            return AtomicNode(token)
        
        raise Exception(f"Error Sintáctico: Esperaba Nodo de Audio, encontré '{token.value}' en línea {token.line}")

    def parse_routing(self):
        left = self.parse_atom()
        if self.current_token and self.current_token.kind == 'T_ARROW':
            op = self.eat('T_ARROW')
            right = self.parse_routing()
            return AudioRouteNode(left, op, right)
        return left

    def parse_function_decl(self):
        self.eat('T_FUNCTION')
        name_token = self.eat('T_USER_FUN')
        self.eat('T_LPAREN')
        
        params = []
        if self.current_token and self.current_token.kind == 'T_VAR_ID':
            params.append(self.eat('T_VAR_ID').value)
            while self.current_token and self.current_token.kind == 'T_COMMA':
                self.eat('T_COMMA')
                params.append(self.eat('T_VAR_ID').value)
                
        self.eat('T_RPAREN')
        self.eat('T_LBRACE')
        
        body_statements = []
        while self.current_token and self.current_token.kind != 'T_RBRACE':
            body_statements.append(self.parse_statement())
            
        self.eat('T_RBRACE')
        return FunctionDeclNode(name_token, params, body_statements)

    def parse_ui_layout(self):
        self.eat('T_LAYOUT')
        self.eat('T_LBRACE')
        widgets = []
        
        ui_tokens = ['T_KNOB', 'T_SWITCH', 'T_SLIDER', 'T_LABEL']
        while self.current_token and self.current_token.kind != 'T_RBRACE':
            if self.current_token.kind in ui_tokens:
                widget_token = self.current_token
                self.advance()
                widgets.append(self.parse_module_call(widget_token))
            else:
                raise Exception(f"Elemento UI inválido '{self.current_token.value}' en línea {self.current_token.line}")
                
        self.eat('T_RBRACE')
        return UILayoutNode(widgets)

    def parse_if_statement(self):
        self.eat('T_IF')
        self.eat('T_LPAREN')
        
        left = self.parse_atom()
        op_tokens = ['T_EE', 'T_GE', 'T_LE', 'T_NE', 'T_GT', 'T_LT']
        if self.current_token and self.current_token.kind in op_tokens:
            op = self.current_token
            self.advance()
            right = self.parse_atom()
            condition = ConditionNode(left, op, right)
        else:
            raise Exception("Se esperaba operador lógico en condición if")
            
        self.eat('T_RPAREN')
        self.eat('T_LBRACE')
        
        true_body = []
        while self.current_token and self.current_token.kind != 'T_RBRACE':
            true_body.append(self.parse_statement())
        self.eat('T_RBRACE')
        
        false_body = None
        if self.current_token and self.current_token.kind == 'T_ELSE':
            self.eat('T_ELSE')
            self.eat('T_LBRACE')
            false_body = []
            while self.current_token and self.current_token.kind != 'T_RBRACE':
                false_body.append(self.parse_statement())
            self.eat('T_RBRACE')
            
        return IfNode(condition, true_body, false_body)

    def parse_statement(self):
        token = self.current_token
        
        if token.kind == 'T_FUNCTION':
            return self.parse_function_decl()
        if token.kind == 'T_LAYOUT':
            return self.parse_ui_layout()
        if token.kind == 'T_IF':
            return self.parse_if_statement()
        if token.kind == 'T_RETURN':
            self.eat('T_RETURN')
            return ReturnNode(self.parse_routing())
            
        next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        if token.kind == 'T_VAR_ID' and next_token and next_token.kind == 'T_ASSIGN':
            target_name = self.eat('T_VAR_ID').value
            self.eat('T_ASSIGN')
            value = self.parse_routing()
            return AssignmentNode(target_name, value)
            
        return self.parse_routing()

    def parse(self):
        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].kind == 'T_EOF'):
            return "Código vacío"
        
        statements = []
        # NUEVO: Bucle resiliente con manejo de excepciones por cada sentencia
        while self.current_token and self.current_token.kind != 'T_EOF':
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except Exception as e:
                # Si ocurre un error, lo guardamos y entramos en modo pánico
                self.errors.append(str(e))
                self.synchronize()
                
        return ProgramNode(statements)