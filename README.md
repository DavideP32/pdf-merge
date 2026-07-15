# PDF Merger

Unisce tutti i file PDF di una cartella in un unico documento, rispettando l'**ordinamento naturale** dei nomi (`doc1`, `doc2`, `doc10`) invece di quello lessicografico (`doc1`, `doc10`, `doc2`).

Due interfacce sullo stesso motore: una da riga di comando e una grafica. Entrambe distribuibili come eseguibile Windows autonomo, senza Python installato sulla macchina di destinazione.

---

## Indice

- [Caratteristiche](#caratteristiche)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Il sommario](#il-sommario)
- [Creazione degli eseguibili](#creazione-degli-eseguibili)
- [Architettura](#architettura)
- [Come funziona il codice](#come-funziona-il-codice)
- [Note e limitazioni](#note-e-limitazioni)
- [Licenza](#licenza)

---

## Caratteristiche

- **Ordinamento naturale**: `cap1, cap2, cap10` - lo stesso ordine che mostra Esplora Risorse.
- **Sommario opzionale**: bookmark navigabili con una voce per file, attivabili su richiesta.
- **Doppia interfaccia**: CLI per script e automazioni, GUI per l'uso quotidiano.
- **Robusto**: un PDF corrotto o protetto viene saltato con un avviso, senza far fallire il batch.
- **Nessuna dipendenza runtime oltre `pypdf`**: la GUI usa `tkinter`, incluso nella standard library.

---

## Requisiti

- Python 3.9 o superiore
- [`pypdf`](https://pypi.org/project/pypdf/) - manipolazione dei PDF
- `tkinter` - solo per la GUI. Incluso nell'installer ufficiale di Python su Windows e macOS; su Linux va installato a parte (`sudo apt install python3-tk` su Debian/Ubuntu).
- [`pyinstaller`](https://pypi.org/project/pyinstaller/) - solo per creare gli eseguibili

Gli eseguibili compilati non hanno alcun requisito: contengono già interprete e dipendenze.

---

## Installazione

```bash
git clone https://github.com/<utente>/pdf-merger.git
cd pdf-merger

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt          # solo runtime
pip install -r requirements-dev.txt      # runtime + pyinstaller
```

---

## Utilizzo

### GUI

```bash
python gui_main.py
```

Oppure doppio click su `merge_pdf-gui.exe`. La finestra espone:

| Campo | Descrizione |
|---|---|
| Cartella di origine | Percorso dei PDF, con bottone **Sfoglia...** per navigare il filesystem |
| File di destinazione | Nome del PDF risultante (l'estensione `.pdf` viene aggiunta se omessa) |
| Crea sommario | Casella di spunta, disattivata per default |
| Log | Elenco dei file trovati, nel loro ordine di unione, ed eventuali avvisi |
| OK / Annulla | Avvia il merge / chiude il programma |

### CLI

```bash
# Cartella corrente, output "merged.pdf", nessun sommario
python cli_main.py

# Cartella specifica
python cli_main.py "C:\Documenti\Fatture"

# Output personalizzato e sommario attivo
python cli_main.py "C:\Libri\Capitoli" -o libro.pdf --outline

# Senza pausa finale (per script e automazioni)
python cli_main.py --no-pause
```

Con l'eseguibile, `merge_pdf-cli.exe` al posto di `python cli_main.py`. Un doppio click su `merge_pdf-cli.exe` unisce i PDF della cartella in cui l'eseguibile si trova.

### Opzioni della CLI

| Flag | Default | Descrizione |
|---|---|---|
| `folder` (posizionale) | cartella dell'eseguibile | Cartella contenente i PDF |
| `-o`, `--output` | `merged.pdf` | Nome o percorso del file di output |
| `--outline` | disattivato | Crea il sommario |
| `--no-pause` | disattivato | Non attende `INVIO` al termine |
| `--version` | - | Mostra la versione |

### Codici di uscita

| Codice | Significato |
|---|---|
| `0` | Merge completato |
| `1` | Cartella non valida, nessun PDF trovato, o nessun file leggibile |
| `2` | Errore inatteso |

---

## Il sommario

Con `--outline` (CLI) o la casella spuntata (GUI), il PDF risultante riceve un **outline**: l'indice navigabile che i lettori mostrano in una barra laterale - "Sommario" in Edge, "Segnalibri" in Acrobat. Ogni file unito diventa una voce, intitolata col nome del file senza estensione, che punta alla sua prima pagina.

Utile per libri e raccolte di capitoli. Per un documento unico e continuo è di norma superfluo, da cui il default disattivato.

> **Da non confondere con il pannello miniature.** Molti lettori, quando un PDF *non* ha outline, aprono di default il pannello che elenca tutte le pagine come anteprime. Vedere l'elenco completo delle pagine invece dei titoli dei file è precisamente il sintomo di un PDF **senza** sommario - non di un sommario malfunzionante.

Nota tecnica: `pypdf` **preserva** sempre gli outline che i PDF sorgente possiedono già, indipendentemente dal flag. Il flag controlla la creazione di voci *nuove*, una per file. Su PDF sorgente privi di bookmark propri - scansioni, export, pagine singole: il caso più comune - senza il flag il risultato non ha alcun sommario.

---

## Creazione degli eseguibili

> Gli eseguibili vanno compilati **sulla stessa piattaforma di destinazione**: per un `.exe` Windows serve compilare su Windows. PyInstaller non fa cross-compilation.

### Entrambi in un colpo solo (Windows)

```bash
build.bat
```

### Manualmente

```bash
pip install pyinstaller

# Versione CLI (con console)
pyinstaller --onefile --console --name merge_pdf-cli cli_main.py

# Versione GUI (senza console)
pyinstaller --onefile --windowed --name merge_pdf-gui gui_main.py
```

Risultato in `dist/`:

| Eseguibile | Flag | Comportamento |
|---|---|---|
| `merge_pdf-cli.exe` | `--console` | Finestra di terminale con l'output testuale |
| `merge_pdf-gui.exe` | `--windowed` | Solo la finestra grafica, nessuna console |

Le cartelle `build/`, `dist/` e i file `.spec` sono artefatti di compilazione, esclusi dal versionamento.

### Perché due eseguibili e non uno

Un singolo binario dovrebbe scegliere tra `--console` e `--windowed`, e nessuna delle due opzioni serve entrambi gli usi:

- con `--console`, la GUI si trascina dietro una finestra di terminale nera e vuota;
- con `--windowed`, la CLI perde `stdout`: lanciata da terminale non stampa nulla.

Due build eliminano il compromesso. Il costo è nullo, perché la logica sta tutta in `merge_pdf/core.py`: i due eseguibili sono due presentazioni dello stesso motore, non due programmi.

### `--onefile` vs `--onedir`

| | `--onefile` | `--onedir` |
|---|---|---|
| Output | Un singolo `.exe` autocontenuto | Cartella con `.exe` + dipendenze |
| Trasporto | Copi solo l'exe | Devi copiare tutta la cartella |
| Avvio | ~1 s (autoestrazione in una temp dir) | Immediato |
| Falsi positivi antivirus | Più frequenti | Più rari |

### Falsi positivi antivirus

Windows Defender segnala occasionalmente i binari PyInstaller `--onefile`, perché l'autoestrazione a runtime è un pattern condiviso con i packer malevoli. Contromisure, in ordine di efficacia:

1. Firmare il binario con un certificato code-signing.
2. Usare `--onedir`.
3. Aggiungere un'esclusione nell'antivirus (solo per uso interno).

---

## Architettura

```
pdf-merger/
├── merge_pdf/
│   ├── __init__.py         # Export pubblici e versione
│   ├── core.py             # Logica di merge - nessun I/O utente
│   ├── cli.py              # Entry point console
│   └── gui.py              # Entry point tkinter
├── cli_main.py             # Launcher CLI per PyInstaller
├── gui_main.py             # Launcher GUI per PyInstaller
├── build.bat               # Compila entrambi gli eseguibili
├── requirements.txt        # Dipendenze runtime
├── requirements-dev.txt    # Runtime + PyInstaller
├── README.md
├── LICENSE
└── .gitignore
```

Il principio è uno solo: **`core.py` non parla con l'utente.** Non stampa, non chiede input, non conosce né la console né tkinter. Comunica attraverso due canali:

- un callback `on_progress(str)` per i messaggi di avanzamento;
- un oggetto `MergeResult` restituito al chiamante.

La CLI collega il callback a `print`, la GUI lo collega a una text box. Stessa logica, due presentazioni. Se in `core.py` ci fosse anche un solo `print()`, la GUI erediterebbe output che non può mostrare - ed è per questo che la separazione non è estetica ma funzionale: è ciò che rende possibili due eseguibili senza duplicare una riga di logica.

I due `*_main.py` alla radice esistono perché PyInstaller richiede uno *script* come punto di ingresso, non un modulo di package.

---

## Come funziona il codice

### `core.natural_key(path) -> list`

Il cuore dell'ordinamento. Risolve il problema del confronto lessicografico: come stringhe, `"doc10.pdf"` precede `"doc2.pdf"` perché il carattere `'1'` viene prima di `'2'`. Che 10 > 2 è irrilevante finché si confrontano stringhe.

```python
parts = re.split(r"(\d+)", path.name)
return [int(part) if part.isdigit() else part.lower() for part in parts]
```

Il gruppo di cattura `(\d+)` fa sì che `re.split` **mantenga** i separatori numerici nel risultato invece di scartarli:

```
"doc10.pdf" -> ['doc', '10', '.pdf'] -> ['doc', 10, '.pdf']
"doc2.pdf"  -> ['doc', '2',  '.pdf'] -> ['doc', 2,  '.pdf']
```

Il confronto tra liste in Python è element-wise: `'doc' == 'doc'`, poi `2 < 10` come **numeri**. `doc2` precede correttamente `doc10`.

Il `.lower()` rende l'ordinamento case-insensitive, coerente con Windows.

### `core.find_pdfs(folder, output) -> list[Path]`

Raccoglie i PDF e li ordina con `natural_key`. Due dettagli non ovvi:

- **Esclusione dell'output.** Senza il filtro, una seconda esecuzione includerebbe il `merged.pdf` della precedente, raddoppiando le pagine a ogni run. Il confronto usa `resolve()` per normalizzare i percorsi.
- **`iterdir()` invece di `glob("*.pdf")`.** Su Linux `glob` è case-sensitive e mancherebbe `FILE.PDF`. Il filtro su `p.suffix.lower()` rende il comportamento identico ovunque.

### `core.merge_pdfs(folder, output, outline, on_progress) -> MergeResult`

Accumula le pagine in un `PdfWriter` e scrive su disco una sola volta al termine.

```python
writer.append(str(pdf), outline_item=pdf.stem if outline else None)
```

`outline_item` è il parametro che **crea** la voce di sommario. Senza, `append()` si limita a preservare gli outline preesistenti del sorgente. `pdf.stem` è il nome senza estensione: `capitolo1` invece di `capitolo1.pdf`.

Altri due punti:

- ogni `append` è in un `try/except`: un PDF corrotto o protetto viene registrato in `skipped` e saltato, senza far fallire il batch;
- `writer.close()` sta in un `finally` perché rilascia gli handle dei file sorgente aperti da `append()`, e va eseguito anche se la scrittura fallisce.

### `core.MergeResult`

Una dataclass invece di un semplice `bool` perché i chiamanti hanno bisogno di cose diverse: la CLI vuole un exit code, la GUI vuole un messaggio da mostrare in una dialog con il conteggio dei file saltati. Il metodo `summary()` produce il riepilogo testuale, riusabile da entrambe.

### `core.base_dir() -> Path`

Cartella di default quando l'utente non ne specifica una, e gestisce una particolarità di PyInstaller:

```python
if getattr(sys, "frozen", False):
    return Path(sys.executable).parent
return Path.cwd()
```

In un bundle `--onefile` l'eseguibile si autoestrae in una cartella temporanea e `__file__` punta **lì dentro**, non dove risiede il `.exe`. `sys.executable` punta sempre al `.exe` reale - esattamente ciò che serve quando l'utente fa doppio click sull'eseguibile posato nella cartella dei PDF.

`sys.frozen` esiste **solo** dentro un bundle PyInstaller: è il modo standard per distinguere l'esecuzione da sorgente da quella da eseguibile.

### `core.resolve_output(folder, output) -> Path`

Un nome relativo viene creato dentro la cartella dei PDF, un percorso assoluto è rispettato com'è. Aggiunge `.pdf` se manca, così nella GUI si può digitare solo `libro`.

### `gui.MergeApp`

Un dettaglio non ovvio, il threading. Il merge di molti PDF può durare secondi; eseguito nel thread principale bloccherebbe il loop di tkinter e Windows mostrerebbe la finestra come "non risponde". Il lavoro va quindi in un thread daemon separato.

Questo però introduce il vincolo inverso: **i widget tkinter non sono thread-safe** e non possono essere toccati da un thread secondario. Da cui il pattern:

```python
on_progress=lambda msg: self.after(0, self._log, msg)
```

`after(0, ...)` accoda la chiamata sul thread della UI, l'unico autorizzato a modificare i widget. Lo stesso vale per `_finish` e `_fail`.

### `__init__.py`

Non importa `gui.py`. `tkinter` non è disponibile ovunque (server headless, alcune distribuzioni Linux) e un import in cima al package farebbe fallire anche il solo uso della CLI.

---

## Note e limitazioni

- **PDF protetti da password**: vengono saltati con un avviso. `pypdf` supporta la decrittazione ma la funzionalità non è esposta.
- **Nessuna ricorsione**: solo i PDF nella cartella indicata, non nelle sottocartelle.
- **Memoria**: le pagine sono accumulate in RAM prima della scrittura. Per merge molto grandi (centinaia di MB) il consumo può essere significativo.
- **Metadati**: il PDF risultante non eredita i metadati dei sorgenti.
- **Sommario a un livello**: una voce per file, senza gerarchia. Eventuali bookmark interni dei sorgenti vengono annidati sotto la rispettiva voce.

---

## Licenza

MIT - vedi [LICENSE](LICENSE).
