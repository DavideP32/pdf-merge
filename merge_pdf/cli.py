"""
cli.py - Interfaccia a riga di comando.

Sottile per costruzione: interpreta gli argomenti, collega il callback di
progresso a print() e traduce il MergeResult in un exit code. Tutta la
logica vive in core.py.
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import base_dir, merge_pdfs, resolve_output


def parse_args(argv=None) -> argparse.Namespace:
    """Definisce e interpreta gli argomenti da riga di comando."""
    parser = argparse.ArgumentParser(
        prog="merge_pdf",
        description="Unisce i PDF di una cartella in un unico file, in ordine naturale.",
    )
    parser.add_argument(
        "folder",
        nargs="?",      # argomento opzionale
        default=None,   # None -> risolto con base_dir() in main()
        help="Cartella contenente i PDF (default: cartella dell'eseguibile).",
    )
    parser.add_argument(
        "-o", "--output",
        default="merged.pdf",
        help="Nome o percorso del PDF di output (default: merged.pdf).",
    )
    parser.add_argument(
        "--outline",
        action="store_true",
        help="Crea un sommario (bookmark) con una voce per ogni file unito.",
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Non attende INVIO al termine (utile in script e automazioni).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Entry point della CLI. Ritorna il codice di uscita del processo."""
    args = parse_args(argv)

    folder = Path(args.folder).resolve() if args.folder else base_dir().resolve()
    output = resolve_output(folder, args.output)

    try:
        # Il callback collega il progresso del core allo stdout.
        result = merge_pdfs(folder, output, outline=args.outline, on_progress=print)
        exit_code = 0 if result.success else 1
        print(result.summary())
    except Exception as exc:
        print(f"Errore inatteso: {exc}")
        exit_code = 2

    # Con il doppio click la console si chiuderebbe subito, rendendo
    # invisibile qualsiasi messaggio. La pausa mantiene la finestra aperta.
    if not args.no_pause:
        input("\nPremi INVIO per uscire...")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
