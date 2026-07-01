"""
Random Student Number Generator
================================

A desktop application for randomly selecting students by number,
built with PySide6 (Qt for Python).

Features
--------
- CSV-based class roster loading
- Random student selection with optional deduplication
- Edge-hiding mode with animated floating window
- Light/Dark theme switching
- Multi-language support (English, 中文简体, 中文繁體, 日本語, 한국어)

Package Structure
-----------------
src/
    __init__.py    Package metadata (version, author).
    __main__.py    Entry point for ``python -m src``.
    app.py         Lightweight coordinator (Main class, main function).
    ui.py          GUI components (MainWindow, FloatingWindow).
    picker.py      Random student selection logic (StudentPicker).
    edge_hider.py  Edge-hiding behaviour (EdgeHider).
    animation.py   Window show/hide animations (Animation).
    tools.py       Utility functions (restart, settings I/O, signal handler).
    constant.py    Path definitions and application-wide constants.

Usage
-----
Run as a module::

    python -m src

Or install and launch programmatically::

    from .app import main
    main()

License
-------
MIT License. See LICENSE file for details.
"""

# Package version — also read by pyproject.toml via setuptools dynamic version.
# Do NOT import heavy dependencies (e.g. PySide6) in this file,
# otherwise setuptools will fail during build without the GUI runtime installed.
__version__ = '1.1.0'
__author__ = 'nanocode38'