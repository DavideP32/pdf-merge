# PDF Toolkit

Un semplice strumento per unire più file PDF presenti in una cartella in un unico file, ordinandoli in modo naturale (`file2.pdf` prima di `file10.pdf`). Disponibile sia come interfaccia grafica (GUI) sia come applicazione da riga di comando (CLI).

## Caratteristiche

- Unione di tutti i file `.pdf` presenti in una cartella
- Ordinamento naturale dei file (l'ordine numerico è rispettato: 1, 2, 10 e non 1, 10, 2)
- Creazione opzionale di un **outline** (segnalibri) con un elemento per ogni PDF di origine, nominato in base al nome del file
- Il file risultante viene salvato in una sottocartella `merged/` dentro la cartella di origine
- Due interfacce: grafica (GUI) e a riga di comando (CLI)

## Requisiti

- Python 3.x
- Dipendenze:

```bash
pip install pypdf sv-ttk
```

> `sv-ttk` serve solo per la GUI (tema Windows 11). Per la sola CLI è sufficiente `pypdf`.

## Struttura del progetto

```bash
.
├── core.py # logica di unione, ordinamento e validazione
├── gui.py # interfaccia grafica (Tkinter)
└── cli.py # interfaccia a riga di comando (argparse)
```

## Utilizzo

### Interfaccia grafica (GUI)

Avvia l'applicazione:

```bash
python gui.py
```

Poi:

1. Clicca su **Select Folder** e scegli la cartella contenente i PDF da unire.
2. Inserisci il nome del file di output nel campo **Output File Name** (l'estensione `.pdf` viene aggiunta automaticamente se mancante).
3. (Opzionale) Spunta **Create Outline** per generare i segnalibri.
4. Clicca su **OK** per avviare l'unione.

Al termine comparirà un messaggio con il percorso del file creato.

### Riga di comando (CLI)

```bash
python cli.py [-o NOME_OUTPUT] [--outline] CARTELLA
```

**Argomenti:**

| Argomento          | Descrizione                                                        |
|--------------------|-------------------------------------------------------------------|
| `folder`           | (obbligatorio) Cartella di origine contenente i PDF da unire      |
| `-o`, `--output`   | Nome del file unito (default: `merged.pdf`)                        |
| `--outline`        | Aggiunge l'outline (segnalibri) al PDF unito                       |
| `-h`, `--help`     | Mostra il messaggio di aiuto                                       |

**Esempi:**

```bash
# Unione base: crea merged.pdf nella cartella ./documenti/merged/
python cli.py ./documenti

# Nome di output personalizzato
python cli.py -o report_completo.pdf ./documenti

# Con outline (segnalibri)
python cli.py -o report.pdf --outline ./documenti
```

## Output

Il file unito viene sempre salvato in una sottocartella `merged/` all'interno della cartella di origine:

```bash
documenti/
├── file1.pdf
├── file2.pdf
├── file10.pdf
└── merged/
    └── report.pdf
```

## Note

- Il nome del file di output **non** può contenere separatori di percorso (`/` o `\`).
- Se nella cartella non è presente alcun PDF, il programma segnala l'errore e si interrompe.
- La sottocartella `merged/` viene creata automaticamente se non esiste (i file esistenti al suo interno non vengono rimossi).

## Codici di uscita (CLI)

| Codice | Significato                          |
|--------|-------------------------------------|
| `0`    | Successo                             |
| `1`    | Errore nel nome file o cartella non valida |
| `3`    | Errore durante la lettura/unione dei PDF |


## Creazione di un eseguibile portabile (.exe)

Puoi generare un singolo `.exe` autonomo con [PyInstaller](https://pyinstaller.org/), senza che l'utente finale debba installare Python o le dipendenze.

Installa PyInstaller:

```bash
pip install pyinstaller
```

### GUI

```bash
pyinstaller --onefile --windowed --collect-all sv_ttk --name merge_pdf-gui gui_main.py
```

| Flag                    | Perché serve                                                                 |
|-------------------------|------------------------------------------------------------------------------|
| `--onefile`             | Impacchetta tutto in un unico `.exe` invece di una cartella con molti file  |
| `--windowed`            | Non apre la console nera all'avvio                                            |
| `--collect-all sv_ttk`  | Include i file di tema di `sv-ttk`, che altrimenti PyInstaller non rileva perché caricati a runtime e non via `import` diretto |
| `--name merge_pdf-gui`  | Nome dell'eseguibile prodotto                                                 |

L'eseguibile finale si troverà nella cartella `dist/`.

### CLI

Per la versione a riga di comando ometti `--windowed` (la console qui serve) e `--collect-all sv_ttk` (la CLI non usa il tema):

```bash
pyinstaller --onefile --name merge_pdf-cli cli.py
```