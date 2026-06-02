import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

if __name__ == "__main__":
    # --- TRUCO PARA WINDOWS ---
    # Esto fuerza a Windows a separar el IDE del ejecutable de Python 
    # para que tu logo aparezca correctamente en la barra de tareas.
    try:
        myappid = 'ferharo03.bypass.ide.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass # Por si se ejecuta en Mac o Linux
    # ---------------------------

    app = QApplication(sys.argv)
    
    # Configurar el ícono global de la aplicación
    app.setWindowIcon(QIcon("assets/bypass_logo.png"))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())