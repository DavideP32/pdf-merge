#!/usr/bin/env python3
"""
Launcher della versione GUI.

PyInstaller ha bisogno di uno script come punto di ingresso, non di un
modulo di package: questo file esiste solo per fornirglielo.
"""

import sys

from merge_pdf.gui import main

if __name__ == "__main__":
    sys.exit(main())
