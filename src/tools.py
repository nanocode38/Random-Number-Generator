import json
import os
import platform
import subprocess
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .constant import LANGUAGE_DIR, DATA_FILE, DEBUG
from .logger import logger

# Default settings used when data.json is missing or corrupted
_DEFAULT_SETTINGS = {
    'Deduplication mode': False,
    'Edge hiding mode': False,
    'Language': 'English',
    'Mode': 'Light',
    'Class': 'example'
}

def restart():
    """Restart The Program"""
    logger.info("Restarting application")
    program = sys.executable
    args = sys.argv[:]

    if args and args[0].endswith('__main__.py'):
        package_dir = os.path.dirname(os.path.abspath(args[0]))
        package_name = os.path.basename(package_dir)
        parent_dir = os.path.dirname(package_dir)
        args = ['-m', package_name] + args[1:]
        logger.debug("Restart as module: %s %s", program, args)
    else:
        parent_dir = None
        logger.debug("Restart as script: %s %s", program, args)

    try:
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen([program] + args, startupinfo=startupinfo, cwd=parent_dir)
        else:
            subprocess.Popen([program] + args, cwd=parent_dir)
        logger.debug("New process spawned successfully")
    except Exception as e:
        logger.error("Failed to spawn new process for restart: %s", e, exc_info=True)
        QMessageBox.critical(None, "Error", f"Restart failed: {e}")
    finally:
        logger.info("Quitting current application instance")
        QApplication.quit()

def sigint_handler(*args):
    logger.info("Received SIGINT (Ctrl+C), initiating graceful shutdown")
    sys.stderr.write('\rReceive KeyboardInterrupt, exiting...\n')
    QApplication.quit()

def load_settings():
    logger.debug("Loading settings from: %s", DATA_FILE)
    try:
        with open(DATA_FILE, encoding='utf-8') as f:
            settings = json.load(f)
        logger.debug("Settings loaded successfully: %s", settings)
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Failed to load settings (%s: %s), falling back to defaults", type(e).__name__, e)
        if DEBUG:
            sys.stderr.write(f'Warning: failed to load settings ({e}), using defaults\n')
        write_settings(**_DEFAULT_SETTINGS)
        return dict(_DEFAULT_SETTINGS)

def write_settings(is_deduplication_mode, is_edge_hiding_mode, mode, language, class_):
    logger.debug("Writing settings to: %s (dedup=%s, edge_hiding=%s, mode=%s, language=%s, class=%s)",
                 DATA_FILE, is_deduplication_mode, is_edge_hiding_mode, mode, language, class_)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'Deduplication mode': is_deduplication_mode,
            'Edge hiding mode': is_edge_hiding_mode,
            'Language': language,
            'Mode': mode,
            'Class': class_
        }, f)
    logger.debug("Settings written successfully")

def load_language(lang):
    lang_path = LANGUAGE_DIR / f'{lang}.json'
    logger.debug("Loading language file: %s", lang_path)
    with open(lang_path, encoding='utf-8') as f:
        data = json.load(f)
    logger.debug("Language file loaded: %s (%d keys)", lang, len(data))
    return data
