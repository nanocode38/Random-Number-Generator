<div align="center">

# Random Student Number Generator

A modern desktop application for randomly selecting students by number, built for teachers who need fair and efficient classroom randomization.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.11+-41CD52?logo=qt&logoColor=white)](https://www.qt.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/nanocode38/Random-Number-Generator/releases)

[Features](#features) · [Installation](#installation) · [Usage](#usage) · [Development](#development) · [Contributing](#contributing)

</div>

---

> **中文版本**请移步 [README-chinese.md](README-chinese.md)

## Overview

Random Student Number Generator is a cross-platform desktop app that helps teachers randomly pick students during class. Load your class roster from a CSV file, click a button, and get a random student — with optional deduplication to make sure everyone gets a turn.

Built with **PySide6** (Qt for Python), it ships with smooth edge-hiding animations, 8 built-in themes, and 5-language support out of the box.

## Features

- **CSV Class Rosters** — Load student lists from simple CSV files. Supports both single-row (names only) and dual-row (numbers + names) formats.
- **Smart Deduplication** — Enable dedup mode to ensure every student is picked fairly. Auto-resets when all students have been selected.
- **Edge-Hide Mode** — Drag the window to a screen edge and it auto-minimizes into a floating icon with a smooth animation. Hover or click to restore — perfect for presentations.
- **8 Themes** — Light, Dark, Ocean, Sunset, Forest, Cyber, Lavender, and Nord. Switch instantly from the menu.
- **Multi-Language** — English, 中文(简体), 中文(繁體), 日本語, 한국어. Add more by dropping a JSON file into the language directory.
- **Cross-Platform** — Runs on Windows, macOS, and Linux thanks to Qt.
- **Settings Persistence** — Your theme, language, class, and mode preferences are saved automatically.

## Installation

### Option A: Download Pre-built Release (Windows)

1. Go to the [Releases page](https://github.com/nanocode38/Random-Number-Generator/releases).
2. Download the latest Windows package (`.zip`).
3. Extract and run `StudentNumberGenerator.exe`.

### Option B: Run from Source

**Prerequisites:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/nanocode38/Random-Number-Generator.git
cd Random-Number-Generator

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install PySide6

# Run the app
python enter.py
# or: python -m src
```

## Usage

### 1. Prepare Your Class Roster

Create a CSV file named after your class (e.g., `ClassA.csv`) and place it in the `Classes/` directory.

**Format A — Names only (single row):**

```csv
Alice, Bob, Charlie, Diana, Evan
```

Student numbers will be auto-assigned as 1, 2, 3, ...

**Format B — Numbers + names (two rows):**

```csv
1, 2, 3, 4, 5
Alice, Bob, Charlie, Diana, Evan
```

> See `Classes/example.csv` for a working example.

### 2. Launch the App

Run the program. Use the **Class** dropdown to select your roster.

### 3. Generate Random Student

Click the **Generate** button to randomly pick a student. Their number and name will be displayed.

### 4. Deduplication Mode

Check the **Deduplication** checkbox to ensure no student is picked twice until everyone has had a turn. When all students have been drawn, the list resets automatically.

### 5. Edge-Hide Mode

Check the **Edge Hide** checkbox to enable window pinning and edge-hiding:

- The window stays on top of all other windows.
- Drag it near the left or right screen edge — after a brief delay it animates into a small floating icon.
- Hover over or click the icon to restore the full window.

This is ideal for presentations where you need the picker nearby but out of the way.

### 6. Themes & Language

- **Theme:** Go to the menu bar → **Theme** → pick from 8 available themes.
- **Language:** Go to the menu bar → **Language** → select your preferred language. The app will restart to apply the change.

## Project Structure

```
Random student number generator/
├── enter.py                 # Entry point script
├── src/
│   ├── __init__.py          # Package metadata (version, author)
│   ├── __main__.py          # Entry point for `python -m src`
│   ├── app.py               # Main coordinator (Main class, main())
│   ├── ui.py                # GUI components (MainWindow, FloatingWindow)
│   ├── picker.py            # Random student selection logic (StudentPicker)
│   ├── edge_hider.py        # Edge-hiding behavior (EdgeHider)
│   ├── animation.py         # Window show/hide animations (Animation)
│   ├── tools.py             # Utilities (restart, settings I/O, language loading)
│   └── constant.py          # Path definitions and app-wide constants
├── AppData/
│   ├── icon.ico / icon.png  # App icons
│   ├── data.json            # Persisted user settings
│   ├── style/               # Theme CSS files (Light, Dark, Ocean, ...)
│   └── language/            # Language JSON files (English, 中文, 日本語, ...)
├── Classes/                 # CSV class roster files
│   └── example.csv
├── Web/                     # Project landing page
├── test/                    # Test suite (pytest)
├── pyproject.toml           # Project config & dependencies
├── update.bat               # Nuitka build script (Windows)
└── update.py                # Web HTML version injector
```

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"
# or manually:
pip install PySide6 black isort autoflake pytest pytest-mock pytest-cov
```

### Running Tests

```bash
pytest
```

Tests are located in the `test/` directory and cover the picker logic, tools, and constants.

### Code Style

The project uses [Black](https://github.com/psf/black) (line length 120), [isort](https://pyc.github.io/isort/), and [autoflake](https://github.com/PyCQA/autoflake) for code formatting:

```bash
black src/ test/
isort src/ test/
autoflake --in-place --remove-unused-imports --remove-unused-variables src/
```

### Building from Source (Windows)

The project is packaged using [Nuitka](https://nuitka.net/):

```bash
# Install Nuitka first
pip install nuitka

# Run the build script
update.bat
```

This produces `dist/StudentNumberGenerator.exe` along with all required runtime files.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before getting started.

### Adding a New Language

1. Copy `AppData/language/English.json` and rename it to your language (e.g., `Français.json`).
2. Translate all the values.
3. Select the new language from the in-app **Language** menu.

### Adding a New Theme

1. Create a new CSS file in `AppData/style/` (e.g., `MyTheme.css`).
2. Style the widgets using Qt Style Sheets. You can reference existing themes like `Light.css` or `Dark.css`.
3. (Optional) Add a theme preview image as `check_mytheme.png`.
4. The theme will automatically appear in the in-app **Theme** menu.

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

## Author

**nanocode38**

- GitHub: [@nanocode38](https://github.com/nanocode38)
- Email: nanocode38@88.com
- Project: [Random-Number-Generator](https://github.com/nanocode38/Random-Number-Generator)

---

<div align="center">

Built with PySide6 & ❤️

</div>
