from pathlib import Path
from pypdf import PdfWriter
import re

def natural_sort(element): 
    file_name = element.name
    # converte il testo a int se è solo numeri, altrimenti tutto in lowercase
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    # splitta i numeri dalle parole e le converte secondo il criterio di convert
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return alphanum_key(file_name)
    

p = Path('test-pdf')
files = list(p.glob('*.pdf'))
sorted_files = sorted(files, key=natural_sort)
print(sorted_files)

merger = PdfWriter()

for pdf in sorted_files:
    merger.append(pdf)

merger.write(p / "merged.pdf")

merger.close()