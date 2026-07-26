from pathlib import Path
from pypdf import PdfWriter #, PdfReader
from pypdf.errors import PdfStreamError
import sys
import re

class MergeError(Exception): pass
class WrongFileNameError(Exception): pass

# ------------------------ SORTING FUNCTIONS -------------------------------- #

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

# ------------------------- VALIDATE OUTPUT FILE NAME ------------------------ #
def validate_output_file_name(output_file_name):
    if ("/" in output_file_name or "\\" in output_file_name):
        raise WrongFileNameError("Output file name should not contain path separators.") 


# ------------------------------- CREATE & SORT ------------------------------ #
def create_directory(path_input_files, output_folder_name):
    output_path = path_input_files / output_folder_name
    output_path.mkdir(exist_ok=True)
    return output_path

def sort_files(list_of_files):
    sorted_files = sorted(list_of_files, key=natural_sort)
    return sorted_files

# -------------------------------- MERGE FILES ------------------------------- #
def merge_pdf(sorted_files, is_create_outline, output_path, output_file_name):
    merger = PdfWriter()
    for pdf in sorted_files:
        try:
            # Add the PDF to the merger, optionally adding an outline item
            merger.append(pdf, outline_item=pdf.stem if is_create_outline else None)
        except PdfStreamError as e:
            merger.close()
            raise MergeError(f"Error while appending PDF file: {pdf}") from e

    # ---------------------------- CREATE FILE IN PATH --------------------------- #

    merger.write(output_path / output_file_name)

    merger.close()