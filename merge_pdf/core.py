"""
core.py - Logica di business del merge.

Questo modulo e' volutamente "puro": non stampa nulla, non chiede input,
non conosce ne' la console ne' tkinter. Tutta la comunicazione verso
l'esterno passa da due canali:

  - un callback `on_progress(str)` per i messaggi di avanzamento;
  - un oggetto `MergeResult` restituito al chiamante.

E' questa separazione che permette a cli.py e gui.py di condividere lo
stesso identico codice di merge presentandolo in due modi diversi: la CLI
collega il callback a print(), la GUI lo collega a una text box. Se qui
dentro ci fosse anche un solo print(), la GUI erediterebbe output che non
puo' mostrare.
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from pypdf import PdfWriter

__all__ = ["natural_key", "find_pdfs", "merge_pdfs", "MergeResult", "base_dir"]

# Tipo del callback di progresso: riceve una riga di testo, non ritorna nulla.
ProgressCallback = Callable[[str], None]


# ---------------------------------------------------------------------------
# Risultato
# ---------------------------------------------------------------------------

@dataclass
class MergeResult:
    """
    Esito di un'operazione di merge.

    Un oggetto risultato invece di un semplice bool perche' i chiamanti hanno
    bisogno di dettagli diversi: la CLI vuole un exit code, la GUI vuole un
    messaggio da mostrare in una dialog con il conteggio dei file saltati.
    """

    success: bool
    output: Optional[Path] = None
    merged: int = 0
    total: int = 0
    skipped: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def summary(self) -> str:
        """Riepilogo testuale, riusabile da qualsiasi interfaccia."""
        if not self.success:
            return self.error or "Merge non riuscito."

        lines = [f"Completato: {self.merged}/{self.total} file uniti."]
        if self.skipped:
            lines.append(f"File saltati: {len(self.skipped)}")
        lines.append(f"Output: {self.output}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Ordinamento naturale
# ---------------------------------------------------------------------------

def natural_key(path: Path) -> List:
    """
    Costruisce una chiave di ordinamento "naturale" per un nome di file.

    Il problema: l'ordinamento lessicografico confronta i nomi carattere per
    carattere, quindi "doc10.pdf" precede "doc2.pdf" perche' il carattere
    '1' < '2'. Che 10 > 2 e' irrilevante: sono stringhe, non numeri.

    La soluzione: spezzare il nome in parti alternate testo/numero e
    convertire le seconde in int. Il confronto tra liste in Python e'
    element-wise, quindi i numeri vengono confrontati come numeri.

        "doc10.pdf" -> ['doc', 10, '.pdf']
        "doc2.pdf"  -> ['doc', 2, '.pdf']

    Confronto: 'doc' == 'doc', poi 2 < 10  ->  doc2 precede doc10. Corretto.
    """
    # Il gruppo di cattura (\d+) fa si' che re.split MANTENGA i separatori
    # numerici nel risultato invece di scartarli:
    #   "doc10.pdf" -> ['doc', '10', '.pdf']
    parts = re.split(r"(\d+)", path.name)

    # .lower() sulle parti testuali -> ordinamento case-insensitive,
    # coerente con il comportamento di Windows.
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def find_pdfs(folder: Path, output: Path) -> List[Path]:
    """
    Restituisce i PDF della cartella, ordinati naturalmente.

    Il file di output viene escluso: senza questo filtro, una seconda
    esecuzione nella stessa cartella includerebbe il merged.pdf prodotto
    dalla precedente, raddoppiando le pagine a ogni run. resolve() normalizza
    i path (link simbolici, percorsi relativi, maiuscole su Windows) prima
    del confronto.
    """
    # iterdir() + filtro sul suffisso invece di glob("*.pdf"): su Linux glob
    # e' case-sensitive e si perderebbe "FILE.PDF". Cosi' e' portabile.
    candidates = [
        p for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".pdf"
        and p.resolve() != output.resolve()
    ]
    return sorted(candidates, key=natural_key)


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_pdfs(
    folder: Path,
    output: Path,
    outline: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> MergeResult:
    """
    Unisce i PDF di `folder` scrivendo il risultato in `output`.

    Args:
        folder:      cartella contenente i PDF da unire.
        output:      percorso del file risultante.
        outline:     se True, crea una voce di sommario (bookmark) per ogni
                     file unito, usando il nome del file come titolo.
        on_progress: callback opzionale per i messaggi di avanzamento.

    Returns:
        Un MergeResult con l'esito dell'operazione.
    """
    # Callback no-op se il chiamante non ne fornisce uno: evita di dover
    # controllare `if on_progress:` a ogni chiamata.
    emit = on_progress or (lambda _msg: None)

    if not folder.is_dir():
        return MergeResult(success=False, error=f"'{folder}' non e' una cartella valida.")

    pdf_files = find_pdfs(folder, output)
    if not pdf_files:
        return MergeResult(success=False, error=f"Nessun file PDF trovato in: {folder}")

    emit(f"Trovati {len(pdf_files)} file PDF.")
    emit("Ordine di unione:")
    for i, pdf in enumerate(pdf_files, start=1):
        emit(f"  {i:>3}. {pdf.name}")
    emit("")

    writer = PdfWriter()
    merged = 0
    skipped: List[str] = []

    for pdf in pdf_files:
        try:
            # outline_item CREA una nuova voce di sommario col titolo dato,
            # sotto cui vengono annidati eventuali bookmark preesistenti del
            # sorgente. Senza questo parametro, append() si limita a
            # PRESERVARE gli outline dei sorgenti: se i PDF di partenza non
            # ne hanno (caso tipico di scansioni ed export), il risultato
            # esce senza alcun sommario.
            #
            # pdf.stem = nome del file senza estensione, piu' leggibile in
            # un sommario rispetto a "capitolo1.pdf".
            writer.append(str(pdf), outline_item=pdf.stem if outline else None)
            merged += 1
        except Exception as exc:
            # Un PDF corrotto o protetto da password non deve far fallire
            # l'intero batch: lo si segnala e si prosegue.
            skipped.append(pdf.name)
            emit(f"  [ATTENZIONE] File saltato '{pdf.name}': {exc}")

    if merged == 0:
        writer.close()
        return MergeResult(
            success=False,
            total=len(pdf_files),
            skipped=skipped,
            error="Nessun file e' stato unito: tutti i PDF sono risultati illeggibili.",
        )

    try:
        with open(output, "wb") as fh:
            writer.write(fh)
    except OSError as exc:
        writer.close()
        return MergeResult(success=False, error=f"Impossibile scrivere '{output}': {exc}")
    finally:
        # close() rilascia gli handle dei file sorgente aperti da append().
        # Nel finally perche' va eseguito anche se la scrittura fallisce.
        writer.close()

    return MergeResult(
        success=True,
        output=output,
        merged=merged,
        total=len(pdf_files),
        skipped=skipped,
    )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def base_dir() -> Path:
    """
    Cartella di default quando l'utente non ne specifica una.

    Attenzione al comportamento di PyInstaller: in un bundle --onefile
    l'eseguibile si autoestrae in una cartella temporanea e __file__ punta
    li' dentro, non dove risiede il .exe. sys.executable punta invece sempre
    al .exe reale, che e' cio' che serve quando l'utente fa doppio click
    sull'eseguibile posato nella cartella dei PDF.

    sys.frozen esiste SOLO dentro un bundle PyInstaller: e' il modo standard
    per distinguere l'esecuzione da sorgente da quella da eseguibile.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path.cwd()


def resolve_output(folder: Path, output: str) -> Path:
    """
    Risolve il percorso di output.

    Un nome relativo viene creato dentro la cartella dei PDF; un percorso
    assoluto viene rispettato cosi' com'e'. Se manca l'estensione .pdf viene
    aggiunta, cosi' l'utente puo' digitare solo "libro" nella GUI.
    """
    path = Path(output)
    if not path.is_absolute():
        path = folder / path
    if path.suffix.lower() != ".pdf":
        path = path.with_suffix(".pdf")
    return path
