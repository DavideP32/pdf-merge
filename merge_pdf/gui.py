"""
gui.py - Interfaccia grafica minimale (tkinter).

tkinter fa parte della standard library: nessuna dipendenza aggiuntiva e
nessun impatto su requirements.txt.

Come cli.py, questo modulo e' solo presentazione: raccoglie i parametri
dai widget, chiama core.merge_pdfs() e mostra il risultato. Non contiene
logica di merge.
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import base_dir, merge_pdfs, resolve_output

WINDOW_SIZE = "500x500"


class MergeApp(tk.Frame):
    """Finestra principale: cartella di origine, nome output, flag sommario."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padx=16, pady=16)
        self.pack(fill="both", expand=True)

        # --- Stato dei widget -------------------------------------------------
        # Le StringVar/BooleanVar tengono sincronizzati widget e valori:
        # leggere .get() restituisce sempre il contenuto corrente del campo.
        self.folder_var = tk.StringVar(value=str(base_dir()))
        self.output_var = tk.StringVar(value="merged.pdf")
        self.outline_var = tk.BooleanVar(value=False)  # default: nessun sommario

        self._build_widgets()

    # -- Costruzione UI --------------------------------------------------------

    def _build_widgets(self) -> None:
        # Cartella di origine + bottone "Sfoglia..."
        ttk.Label(self, text="Cartella di origine:").pack(anchor="w")
        folder_row = ttk.Frame(self)
        folder_row.pack(fill="x", pady=(2, 10))
        ttk.Entry(folder_row, textvariable=self.folder_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(folder_row, text="Sfoglia...", command=self._browse).pack(
            side="left", padx=(6, 0)
        )

        # Nome del file di destinazione
        ttk.Label(self, text="File di destinazione:").pack(anchor="w")
        ttk.Entry(self, textvariable=self.output_var).pack(fill="x", pady=(2, 10))

        # Flag sommario
        ttk.Checkbutton(
            self,
            text="Crea sommario (una voce per ogni file unito)",
            variable=self.outline_var,
        ).pack(anchor="w", pady=(0, 10))

        # Area di log: mostra cio' che in CLI andrebbe su stdout.
        ttk.Label(self, text="Log:").pack(anchor="w")
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, pady=(2, 10))

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        # state="disabled" rende la text box read-only: l'utente non puo'
        # scriverci dentro. Va riabilitata temporaneamente per inserire testo
        # (vedi _log).
        self.log = tk.Text(
            log_frame, height=8, wrap="word", state="disabled",
            yscrollcommand=scrollbar.set,
        )
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log.yview)

        # Bottoni
        button_row = ttk.Frame(self)
        button_row.pack(fill="x")
        ttk.Button(button_row, text="Annulla", command=self.master.destroy).pack(
            side="right"
        )
        self.ok_button = ttk.Button(button_row, text="OK", command=self._run)
        self.ok_button.pack(side="right", padx=(0, 6))

    # -- Azioni ----------------------------------------------------------------

    def _browse(self) -> None:
        """Apre il selettore di cartelle di sistema."""
        chosen = filedialog.askdirectory(
            title="Seleziona la cartella con i PDF",
            initialdir=self.folder_var.get() or str(base_dir()),
        )
        # askdirectory() ritorna stringa vuota se l'utente annulla: in quel
        # caso il campo non va sovrascritto.
        if chosen:
            self.folder_var.set(chosen)

    def _log(self, message: str) -> None:
        """Aggiunge una riga all'area di log (che e' read-only per l'utente)."""
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")           # scroll automatico all'ultima riga
        self.log.configure(state="disabled")

    def _run(self) -> None:
        """Valida gli input e avvia il merge in un thread separato."""
        folder = Path(self.folder_var.get()).expanduser()
        if not folder.is_dir():
            messagebox.showerror("Errore", f"Cartella non valida:\n{folder}")
            return

        output_name = self.output_var.get().strip()
        if not output_name:
            messagebox.showerror("Errore", "Specificare un nome per il file di destinazione.")
            return

        output = resolve_output(folder.resolve(), output_name)

        # Pulisce il log della run precedente.
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        # Il merge di molti PDF puo' durare secondi: eseguito nel thread
        # principale bloccherebbe il loop di tkinter e la finestra
        # apparirebbe "non risponde". Un thread daemon separato la tiene viva.
        self.ok_button.configure(state="disabled")
        threading.Thread(
            target=self._worker,
            args=(folder.resolve(), output),
            daemon=True,
        ).start()

    def _worker(self, folder: Path, output: Path) -> None:
        """Esegue il merge fuori dal thread della UI."""
        try:
            result = merge_pdfs(
                folder,
                output,
                outline=self.outline_var.get(),
                # I widget tkinter non sono thread-safe: non si possono
                # toccare da un thread secondario. after(0, ...) accoda la
                # chiamata sul thread della UI, che e' l'unico autorizzato.
                on_progress=lambda msg: self.after(0, self._log, msg),
            )
            self.after(0, self._finish, result)
        except Exception as exc:
            self.after(0, self._fail, str(exc))

    def _finish(self, result) -> None:
        """Mostra l'esito. Gira sul thread della UI (via after)."""
        self.ok_button.configure(state="normal")
        self._log(result.summary())

        if result.success:
            messagebox.showinfo("Completato", result.summary())
        else:
            messagebox.showerror("Errore", result.summary())

    def _fail(self, message: str) -> None:
        """Gestisce un'eccezione imprevista. Gira sul thread della UI."""
        self.ok_button.configure(state="normal")
        self._log(f"Errore inatteso: {message}")
        messagebox.showerror("Errore", f"Errore inatteso:\n{message}")


def main() -> int:
    """Entry point della GUI."""
    root = tk.Tk()
    root.title("PDF Merger")
    root.geometry(WINDOW_SIZE)
    root.minsize(420, 420)
    MergeApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
