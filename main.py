from pathlib import Path
from pypdf import PdfWriter

p = Path('test-pdf')
files = list(p.glob('*.pdf'))
print(files)
merger = PdfWriter()

for pdf in files:
    merger.append(pdf)

merger.write("test-pdf/merged.pdf")