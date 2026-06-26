import sys
import platform
import subprocess

from PySide6.QtWidgets import QApplication, QMessageBox

def restart():
    """Restart The Program"""
    program = sys.executable
    args = sys.argv
    try:
        if platform.system() == "Windows":
            # Try to hide the console window (invalid if the program is a console program; if it is a GUI program, it will not be displayed)
            # Use the CREATE_NO_WINDOW flag (Windows only)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE  # 隐藏窗口
            subprocess.Popen([program] + args, startupinfo=startupinfo)
        else:
            subprocess.Popen([program] + args)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Restart failed: {e}")
    finally:
        sys.exit()

def sigint_handler(*args):
    sys.stderr.write('\rReceive KeyboardInterrupt, exiting...\n')
    QApplication.quit()