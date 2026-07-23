from pathlib import Path
from pypdf import PdfWriter #, PdfReader
from pypdf.errors import PdfStreamError
import sys
import argparse
import re

# --------------------------------- FUNCTIONS -------------------------------- #

# sort files with natural sort method
def natural_sort(element): 
    file_name = element.name
    return split_pdf_name(file_name)

# split strings and numbers and convert each of them
def split_pdf_name(name):
    list_parts_name = re.split('([0-9]+)', name)
    new_list = []
    for part in list_parts_name:
        new_list.append(convert_text(part))
    return new_list
        
# Convert text to int if number or lowercase if text
def convert_text(text):
    return int(text) if text.isdigit() else text.lower()

# --------------------------------- ARGPARSE --------------------------------- #

parser = argparse.ArgumentParser(
                    prog='pdf-merge-cli',
                    description='Merge pdfs in a folder',
                    epilog='ciao ciao')

parser.add_argument("-o", "--output", type=str, default="merged.pdf", help="name of the merged file")
parser.add_argument("folder", type=str, help="source folder for the pdfs to be merged")
parser.add_argument("--outline", help="optionally add outline to the merged pdf", action="store_true")
args = parser.parse_args()


output_file_name = args.output

if ("/" in output_file_name or "\\" in output_file_name):
    parser.error("Output file name should not contain path separators.")


# ---------------------------- TAKE AND SORT FILES --------------------------- #

path_input_files = Path(args.folder)

if not path_input_files.is_dir():
    print("The specified folder does not exist or is not a directory.", file=sys.stderr)
    sys.exit(1)

list_of_files = list(path_input_files.glob('*.pdf'))

if not list_of_files:
    print("No PDF file is present in the given folder.", file=sys.stderr)
    sys.exit(1)

output_path = path_input_files / "merged"
output_path.mkdir(exist_ok=True)

sorted_files = sorted(list_of_files, key=natural_sort)

# -------------------------------- MERGE FILES ------------------------------- #

merger = PdfWriter()

for pdf in sorted_files:
    try:
        # Add the PDF to the merger, optionally adding an outline item
        merger.append(pdf, outline_item=pdf.stem if args.outline else None)
    except PdfStreamError as e:
        print(f"Error reading PDF file {pdf}: {e}", file=sys.stderr)
        merger.close()
        sys.exit(3)


# ---------------------------- CREATE FILE IN PATH --------------------------- #

merger.write(output_path / output_file_name)
print(f"Merged PDF saved as {output_path / output_file_name}")

merger.close()