from pathlib import Path
from pypdf import PdfWriter #, PdfReader
import argparse
import re

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

    

parser = argparse.ArgumentParser(
                    prog='pdf-merge-cli',
                    description='Merge pdfs in a folder',
                    epilog='ciao ciao')

parser.add_argument("-o", "--output", type=str, default="merged.pdf", help="name of the merged file")
parser.add_argument("folder", type=str, help="source folder for the pdfs to be merged")
parser.add_argument("--outline", help="optionally add outline to the merged pdf", action="store_true")
args = parser.parse_args()

output_file = args.output

if ("/" in output_file or "\\" in output_file):
    parser.error("Output file name should not contain path separators.")

p = Path(args.folder)
files = list(p.glob('*.pdf'))
sorted_files = sorted(files, key=natural_sort)


merger = PdfWriter()


for pdf in sorted_files:
    # reader = PdfReader(pdf)
    # number_of_pages = len(reader.pages)
    merger.append(pdf, outline_item=pdf.stem if args.outline else None)
    # if (args.outline):
    #     merger.add_outline_item(pdf.stem, len(merger.pages) - number_of_pages)
    # reader.close()

Path(p / "merged").mkdir(exist_ok=True)
merger.write(p / "merged" / output_file)

merger.close()