#!/usr/bin/env python3
"""
Launcher della versione CLI.

PyInstaller ha bisogno di uno script come punto di ingresso, non di un
modulo di package: questo file esiste solo per fornirglielo.
"""

import sys

from merge_pdf.cli import main

if __name__ == "__main__":
    sys.exit(main())
