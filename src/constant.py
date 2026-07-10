import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
print(os.getcwd())

APPDATA_DIR = BASE_DIR / 'AppData'
CLASSES_DIR = BASE_DIR / 'Classes'
DATA_FILE = APPDATA_DIR / 'data.json'
LANGUAGE_DIR = APPDATA_DIR / 'language'
STYLE_DIR = APPDATA_DIR / 'style'


# Constant
WINDOW_OPACITY = 0.9
EDGE_HIDDEN_DELAY_TIME = 1
EDGE_POS_FAULT_TOLERANCE = 5
ROOT_WINDOW_WIDTH = 450
ROOT_WINDOW_HEIGHT = 450
DEBUG = os.path.isfile("DEBUG")

# Animation mode identifiers
MODE_HIDE = 'hide'
MODE_SHOW = 'show'