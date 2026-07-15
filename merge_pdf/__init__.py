"""
PDF Merger - unisce i PDF di una cartella in un unico documento.

Il package e' diviso per responsabilita':
  - core.py : logica di merge, senza alcun I/O verso l'utente
  - cli.py  : entry point a riga di comando
  - gui.py  : entry point grafico (tkinter)

gui.py non e' importato qui: tkinter non e' disponibile su tutti gli
ambienti (es. server headless) e un import in cima al package farebbe
fallire anche il solo uso della CLI.
"""

__version__ = "2.0.0"

from .core import MergeResult, base_dir, find_pdfs, merge_pdfs, natural_key, resolve_output

__all__ = [
    "__version__",
    "MergeResult",
    "base_dir",
    "find_pdfs",
    "merge_pdfs",
    "natural_key",
    "resolve_output",
]
