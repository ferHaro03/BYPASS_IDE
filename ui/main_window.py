import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, 
                             QListWidget, QLabel, QTreeView, QToolBar, 
                             QFileDialog, QStyle)
from PyQt6.QtCore import Qt, QDir, QSize, QRect
from PyQt6.QtGui import QFont, QAction, QIcon, QFileSystemModel, QPainter, QTextFormat, QColor
from core.lexer import LexerBYPASS
from ui.highlighter import BypassHighlighter

# --- CLASE PARA EL ÁREA DE NÚMEROS DE LÍNEA ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)

# --- EDITOR MEJORADO CON NÚMEROS DE LÍNEA ---
class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Conexiones para actualizar el área de números
        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.textChanged.connect(self.line_number_area.update)
        self.cursorPositionChanged.connect(self.line_number_area.update)

        self.update_line_number_area_width()

    def line_number_area_width(self):
        digits = len(str(max(1, self.document().blockCount())))
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e")) # Fondo del margen

        block = self.document().begin()
        block_number = block.blockNumber()
        top = int(self.document().documentLayout().blockBoundingRect(block).top())
        bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
        offset = self.verticalScrollBar().value()

        while block.isValid():
            visible_top = top - offset
            if visible_top >= event.rect().bottom():
                break
            
            if block.isVisible() and visible_top >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#75715E")) # Color del número (gris)
                painter.drawText(0, visible_top, self.line_number_area.width() - 5, 
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
            block_number += 1

# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BYPASS IDE v0.1")
        self.resize(1000, 600)
        self.current_file = None

        self.create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Explorador
        self.file_model = QFileSystemModel()
        root_path = QDir.currentPath()
        self.file_model.setRootPath(root_path)
        self.file_model.setNameFilters(["*.bps"])
        self.file_model.setNameFilterDisables(False)

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(root_path))
        for i in range(1, 4): self.file_tree.hideColumn(i)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)

        # Área de Trabajo
        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal)

        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        file_layout.addWidget(QLabel("EXPLORER"))
        file_layout.addWidget(self.file_tree)

        self.editor_token_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Usamos nuestro nuevo CodeEditor mejorado
        editor_cont = QWidget()
        ed_layout = QVBoxLayout(editor_cont)
        ed_layout.addWidget(QLabel("CODE EDITOR"))
        self.code_editor = CodeEditor() 
        self.highlighter = BypassHighlighter(self.code_editor.document())
        self.code_editor.textChanged.connect(self.run_lexer)
        ed_layout.addWidget(self.code_editor)

        # Tokens
        lexer_cont = QWidget()
        lex_layout = QVBoxLayout(lexer_cont)
        lex_layout.addWidget(QLabel("LEXER OUTPUT"))
        self.token_list = QListWidget()
        self.token_list.setFont(QFont("Consolas", 10))
        lex_layout.addWidget(self.token_list)

        self.editor_token_splitter.addWidget(editor_cont)
        self.editor_token_splitter.addWidget(lexer_cont)
        self.editor_token_splitter.setSizes([700, 250])

        self.workspace_splitter.addWidget(file_panel)
        self.workspace_splitter.addWidget(self.editor_token_splitter)
        self.workspace_splitter.setSizes([200, 1000])

        self.main_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_vertical_splitter.addWidget(self.workspace_splitter)
        
        err_cont = QWidget()
        err_layout = QVBoxLayout(err_cont)
        err_layout.addWidget(QLabel("ERRORS & LOGS"))
        self.error_console = QListWidget()
        self.error_console.setMaximumHeight(200)
        err_layout.addWidget(self.error_console)
        
        self.main_vertical_splitter.addWidget(err_cont)
        self.main_vertical_splitter.setSizes([700, 150])

        main_layout.addWidget(self.main_vertical_splitter)
        self.apply_styles()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        style = self.style()
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Nuevo", self, triggered=self.new_file))
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Carpeta", self, triggered=self.open_directory_dialog))
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Guardar", self, triggered=self.save_file))
        toolbar.addSeparator()
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "RUN", self, triggered=self.compile_project))

    def open_directory_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if path:
            self.file_model.setRootPath(path)
            self.file_tree.setRootIndex(self.file_model.index(path))

    def new_file(self):
        self.code_editor.clear()
        self.current_file = None
        self.setWindowTitle("BYPASS IDE v0.1 - Nuevo")

    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())
            self.current_file = path
            self.setWindowTitle(f"BYPASS IDE v0.1 - {os.path.basename(path)}")
        except Exception as e:
            self.error_console.addItem(f"Error: {str(e)}")

    def save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "BYPASS (*.bps)")
            if not path: return
            self.current_file = path
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
        except Exception as e:
            self.error_console.addItem(str(e))

    def compile_project(self):
        self.error_console.addItem("Iniciando análisis sintáctico...")

    def run_lexer(self):
        code = self.code_editor.toPlainText()
        self.token_list.clear()
        self.error_console.clear()
        if not code.strip(): return
        lexer = LexerBYPASS(code)
        tokens, errores = lexer.tokenize()
        for t in tokens: self.token_list.addItem(str(t))
        for err in errores: self.error_console.addItem(err)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QToolBar { background-color: #1e1e1e; border-bottom: 1px solid #333; spacing: 15px; padding: 5px; }
            QSplitter::handle { background-color: #333; }
            QLabel { color: #E6DB74; font-weight: bold; font-size: 10px; padding-left: 5px; }
            QTextEdit, QListWidget, QTreeView { 
                background-color: #1e1e1e; 
                color: #fff; 
                border: 1px solid #333; 
            }
            QListWidget { color: #A6E22E; }
        """)