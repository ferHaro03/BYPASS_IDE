import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, 
                             QListWidget, QLabel, QTreeView, QToolBar, 
                             QFileDialog, QStyle, QTabWidget)
from PyQt6.QtCore import Qt, QDir, QSize, QRect
from PyQt6.QtGui import QFont, QAction, QIcon, QFileSystemModel, QPainter, QColor
from core.lexer import LexerBYPASS
from ui.highlighter import BypassHighlighter

# --- ÁREA DE NÚMEROS DE LÍNEA ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)

# --- EDITOR DE CÓDIGO ---
class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
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
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        block = self.document().begin()
        block_number = block.blockNumber()
        top = int(self.document().documentLayout().blockBoundingRect(block).top())
        bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
        offset = self.verticalScrollBar().value()
        while block.isValid():
            visible_top = top - offset
            if visible_top >= event.rect().bottom(): break
            if block.isVisible() and visible_top >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#75715E"))
                painter.drawText(0, visible_top, self.line_number_area.width() - 5, 
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
            block_number += 1

# --- VENTANA PRINCIPAL DEL IDE ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BYPASS IDE v0.1")
        self.resize(1000, 650)
        self.current_file = None

        # 1. Crear Toolbar primero para tener las referencias a las acciones
        self.create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 2. Explorador de Archivos (Izquierda)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        for i in range(1, 4): self.file_tree.hideColumn(i)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)
        
        exp_container = QWidget()
        exp_layout = QVBoxLayout(exp_container)
        exp_layout.addWidget(QLabel("EXPLORER"))
        exp_layout.addWidget(self.file_tree)

        # 3. Panel Central con Pestañas RAD (Source, Design, Debug)
        self.center_tabs = QTabWidget()
        self.center_tabs.setTabPosition(QTabWidget.TabPosition.South)

        # Pestaña Source
        self.code_editor = CodeEditor()
        self.highlighter = BypassHighlighter(self.code_editor.document())
        self.code_editor.textChanged.connect(self.run_compiler_pipeline)
        self.center_tabs.addTab(self.code_editor, "Source")

        # Pestaña Design
        self.gui_preview = QWidget()
        self.gui_preview.setStyleSheet("background-color: #252525;")
        design_layout = QVBoxLayout(self.gui_preview)
        design_layout.addWidget(QLabel("GUI DESIGN PREVIEW"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.center_tabs.addTab(self.gui_preview, "Design")

        # Pestaña Debug (Monitoreo)
        self.debug_panel = QWidget()
        self.debug_panel.setStyleSheet("background-color: #121212;")
        debug_layout = QVBoxLayout(self.debug_panel)
        self.scope_area = QWidget()
        self.spectrum_area = QWidget()
        debug_layout.addWidget(QLabel("OSCILLOSCOPE / SPECTRUM ANALYZER"))
        debug_layout.addWidget(self.scope_area)
        debug_layout.addWidget(self.spectrum_area)
        self.center_tabs.addTab(self.debug_panel, "Debug & Test")

        # 4. Panel de Análisis (Derecha)
        self.analysis_tabs = QTabWidget()
        self.token_list = QListWidget()
        self.ast_view = QListWidget()
        self.symbol_table = QListWidget()
        self.analysis_tabs.addTab(self.token_list, "Lexer")
        self.analysis_tabs.addTab(self.ast_view, "Parser")
        self.analysis_tabs.addTab(self.symbol_table, "Semantics")

        analysis_container = QWidget()
        analysis_layout = QVBoxLayout(analysis_container)
        analysis_layout.addWidget(QLabel("COMPILER OUTPUT"))
        analysis_layout.addWidget(self.analysis_tabs)

        self.main_h_splitter.addWidget(exp_container)
        self.main_h_splitter.addWidget(QWidget()) # Contenedor para el centro
        self.main_h_splitter.widget(1).setLayout(QVBoxLayout())
        self.main_h_splitter.widget(1).layout().addWidget(QLabel("WORKSPACE"))
        self.main_h_splitter.widget(1).layout().addWidget(self.center_tabs)
        self.main_h_splitter.addWidget(analysis_container)
        self.main_h_splitter.setSizes([200, 800, 400])

        # 5. Consola Inferior (Errores)
        self.main_v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_v_splitter.addWidget(self.main_h_splitter)
        err_container = QWidget()
        err_layout = QVBoxLayout(err_container)
        err_layout.addWidget(QLabel("ERRORS & LOGS"))
        self.error_console = QListWidget()
        err_layout.addWidget(self.error_console)
        self.main_v_splitter.addWidget(err_container)
        self.main_v_splitter.setSizes([700, 150])

        main_layout.addWidget(self.main_v_splitter)
        self.apply_styles()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        style = self.style()
        
        # Archivos
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Nuevo", self, triggered=self.new_file))
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Carpeta", self, triggered=self.open_directory_dialog))
        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Guardar", self, triggered=self.save_file))
        toolbar.addSeparator()

        # Analizadores (Solo Texto)
        self.parser_act = QAction("Parser", self)
        self.parser_act.setCheckable(True)
        self.parser_act.setChecked(True)
        self.parser_act.triggered.connect(self.run_compiler_pipeline)
        toolbar.addAction(self.parser_act)

        self.sem_act = QAction("Semantics", self)
        self.sem_act.setCheckable(True)
        self.sem_act.setChecked(True)
        self.sem_act.triggered.connect(self.run_compiler_pipeline)
        toolbar.addAction(self.sem_act)
        toolbar.addSeparator()

        # Transporte y Test
        self.load_audio_act = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DriveDVDIcon), "Audio", self)
        self.load_audio_act.triggered.connect(self.load_test_audio)
        toolbar.addAction(self.load_audio_act)

        self.play_act = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "Play", self)
        self.play_act.triggered.connect(self.play_audio_test)
        toolbar.addAction(self.play_act)

        self.stop_act = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaStop), "Stop", self)
        self.stop_act.triggered.connect(self.stop_audio_test)
        toolbar.addAction(self.stop_act)
        toolbar.addSeparator()

        toolbar.addAction(QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "BUILD", self, triggered=self.compile_project))

    def run_compiler_pipeline(self):
        code = self.code_editor.toPlainText()
        self.token_list.clear()
        self.error_console.clear()
        self.ast_view.clear()
        self.symbol_table.clear()
        
        if not code.strip(): return
        
        # Lexer
        lexer = LexerBYPASS(code)
        tokens, errores = lexer.tokenize()
        for t in tokens: self.token_list.addItem(str(t))
        for err in errores: self.error_console.addItem(err)

        # --- FASE 2: PARSER ---
        if self.parser_act.isChecked():
            from core.parser import ParserBYPASS
            parser = ParserBYPASS(tokens)
            ast_result = parser.parse()
            
            self.ast_view.addItem("AST GENERADO:")
            self.ast_view.addItem(str(ast_result))
        else:
            self.ast_view.addItem("Parser: [DESACTIVADO]")

        # Semantics dinámico
        if self.sem_act.isChecked():
            self.symbol_table.addItem("Semantics: Validando...")
        else:
            self.symbol_table.addItem("Semantics: [DESACTIVADO]")

    # Métodos de Soporte
    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path): self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())
            self.current_file = path
            self.setWindowTitle(f"BYPASS IDE v0.1 - {os.path.basename(path)}")
        except Exception as e: self.error_console.addItem(str(e))

    def new_file(self):
        self.code_editor.clear()
        self.current_file = None
        self.setWindowTitle("BYPASS IDE v0.1 - Nuevo")

    def save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "BYPASS (*.bps)")
            if not path: return
            self.current_file = path
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
        except Exception as e: self.error_console.addItem(str(e))

    def open_directory_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if path:
            self.file_model.setRootPath(path)
            self.file_tree.setRootIndex(self.file_model.index(path))

    def load_test_audio(self): self.error_console.addItem("Cargando archivo .wav...")
    def play_audio_test(self): self.center_tabs.setCurrentIndex(2)
    def stop_audio_test(self): self.error_console.addItem("Stop.")
    def compile_project(self): self.error_console.addItem("Generando Binarios...")

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QToolBar { background-color: #1e1e1e; border-bottom: 1px solid #333; spacing: 10px; padding: 5px; }
            QToolBar QToolButton { color: #888; font-weight: bold; font-size: 11px; padding: 4px 8px; }
            QToolBar QToolButton:checked { color: #66D9EF; background-color: #252525; border-radius: 4px; }
            QSplitter::handle { background-color: #333; }
            QLabel { color: #E6DB74; font-weight: bold; font-size: 10px; padding: 2px 5px; }
            
            QTabWidget::pane { border: 1px solid #333; background: #1e1e1e; }
            QTabBar::tab { background: #252525; color: #888; padding: 8px 15px; border: 1px solid #333; }
            QTabBar::tab:selected { background: #1e1e1e; color: #66D9EF; border-bottom: 2px solid #66D9EF; }
            
            QTextEdit, QListWidget, QTreeView { background-color: #1e1e1e; color: #fff; border: 1px solid #333; }
            QListWidget { color: #A6E22E; font-family: 'Consolas'; font-size: 11px; }
        """)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())