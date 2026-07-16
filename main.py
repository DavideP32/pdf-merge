from pathlib import Path
from pypdf import PdfWriter
import argparse
import re

def natural_sort(element): 
    file_name = element.name
    # converte il testo a int se è solo numeri, altrimenti tutto in lowercase
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    # splitta i numeri dalle parole e le converte secondo il criterio di convert
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return alphanum_key(file_name)

parser = argparse.ArgumentParser(
                    prog='pdf-merge-cli',
                    description='Merge pdfs in a folder',
                    epilog='ciao ciao')

parser.add_argument("-o", "--output", type=str, default="merged.pdf", help="name of the merged file")
parser.add_argument("folder", type=str, help="source folder for the pdfs to be merged")
parser.add_argument("--outline", help="optionally add outline to the merged pdf", action="store_true")
args = parser.parse_args()

input_folder = args.folder
output_file = args.output

if ("/" in output_file or "\\" in output_file):
    parser.error("Output file name should not contain path separators.")

p = Path(args.folder)
files = list(p.glob('*.pdf'))
sorted_files = sorted(files, key=natural_sort)


merger = PdfWriter()

for pdf in sorted_files:
    merger.append(pdf)

Path(p / "merged").mkdir(exist_ok=True)
merger.write(p / "merged" / output_file)

merger.close()