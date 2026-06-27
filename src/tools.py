import sys
import platform
import subprocess
import os
import json

from PySide6.QtWidgets import QApplication, QMessageBox

def restart():
    """Restart The Program"""
    program = sys.executable
    args = sys.argv[:]

    if args and args[0].endswith('__main__.py'):
        package_dir = os.path.dirname(os.path.abspath(args[0]))
        package_name = os.path.basename(package_dir)
        parent_dir = os.path.dirname(package_dir)
        args = ['-m', package_name] + args[1:]
    else:
        parent_dir = None

    try:
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen([program] + args, startupinfo=startupinfo, cwd=parent_dir)
        else:
            subprocess.Popen([program] + args, cwd=parent_dir)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Restart failed: {e}")
    finally:
        sys.exit()

def sigint_handler(*args):
    sys.stderr.write('\rReceive KeyboardInterrupt, exiting...\n')
    QApplication.quit()

def load_settings():
    with open('AppData/data.json', encoding='utf-8') as f:
        return json.load(f)

def write_settings(is_deduplication_mode, is_edge_hiding_mode, mode, language):
    with open('AppData/data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'Deduplication mode': is_deduplication_mode,
            'Edge hiding mode': is_edge_hiding_mode,
            'Language': language,
            'Mode': mode
        }, f)

def load_language(lang):
    with open(f'AppData/language/{lang}.json', encoding='utf-8') as f:
        return json.load(f)