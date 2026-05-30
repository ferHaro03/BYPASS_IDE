class Symbol:
    def __init__(self, name, type_class, scope, extra_info=""):
        self.name = name
        self.type_class = type_class  # 'Variable', 'Funcion', 'Módulo'
        self.scope = scope            # 'Global' o nombre de la función
        self.extra_info = extra_info

    def __repr__(self):
        return f"[{self.scope}] {self.name} : {self.type_class} {self.extra_info}"

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = []
        self.current_scope = "Global"
        self.errors = []

    def analyze(self, ast_root):
        """Punto de entrada: Recorre todo el árbol (AST)"""
        if not ast_root or isinstance(ast_root, str): return
        
        # Agregamos los puertos globales por defecto
        self.add_symbol("INPUT", "Puerto", "Global")
        self.add_symbol("OUTPUT", "Puerto", "Global")
        
        self.visit(ast_root)
        return self.symbol_table, self.errors

    def add_symbol(self, name, type_class, scope, extra=""):
        # Verificamos que no exista ya en el mismo scope
        for sym in self.symbol_table:
            if sym.name == name and sym.scope == scope:
                return # Ya está registrado
        self.symbol_table.append(Symbol(name, type_class, scope, extra))

    def visit(self, node):
        """Patrón Visitor para recorrer los nodos"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_AssignmentNode(self, node):
        # Cuando encontramos una asignación (ej. distorsion = Fuzz)
        # Lo agregamos a la tabla de símbolos
        tipo = "Variable"
        # Pequeña inferencia de tipo
        if hasattr(node.value, 'token') and node.value.token.kind in ['T_STRING', 'T_NUMBER']:
            extra = f"(Valor: {node.value.token.value})"
        else:
            extra = "(Instancia de Audio)"
            
        self.add_symbol(node.target, tipo, self.current_scope, extra)
        self.visit(node.value)

    def visit_FunctionDeclNode(self, node):
        # Registramos la función en el entorno global
        func_name = node.name_token.value
        self.add_symbol(func_name, "Función", "Global", f"(Args: {len(node.params)})")
        
        # Cambiamos el scope al interior de la función
        previous_scope = self.current_scope
        self.current_scope = func_name
        
        # Registramos los parámetros como variables locales
        for param in node.params:
            self.add_symbol(param, "Parámetro", self.current_scope)
            
        # Visitamos el cuerpo
        for stmt in node.body:
            self.visit(stmt)
            
        # Restauramos el scope
        self.current_scope = previous_scope

    def visit_ModuleCallNode(self, node):
        # Registramos el uso del módulo
        self.add_symbol(node.token.value, "Módulo Nativo", "Global")

    def visit_AudioRouteNode(self, node):
        self.visit(node.left)
        self.visit(node.right)