from pathlib import Path
import sys
import argparse
from core import validate_and_correct_output_file_name, create_directory, sort_files, merge_pdf, MergeError, WrongFileNameError


def main():
    output_folder_name = "merged"

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

    try:
        output_file_name = validate_and_correct_output_file_name(output_file_name)
    except WrongFileNameError as e:
        print(f"Error with the file name: {e}", file=sys.stderr)
        sys.exit(1)

    # ---------------------------- TAKE AND SORT FILES --------------------------- #

    path_input_files = Path(args.folder)

    if not path_input_files.is_dir():
        print("The specified folder does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    list_of_files = list(path_input_files.glob('*.pdf'))

    if not list_of_files:
        print("No PDF file is present in the given folder.", file=sys.stderr)
        sys.exit(1)


    # ------------------------------ FUNCTION CALLS ------------------------------ #
    output_path = create_directory(path_input_files=path_input_files, output_folder_name=output_folder_name)

    sorted_files = sort_files(list_of_files=list_of_files)

    try:
        merge_pdf(sorted_files=sorted_files,
                is_create_outline=args.outline,
                output_path=output_path, 
                output_file_name=output_file_name)
    except MergeError as e:
        print(f"Error reading PDF file: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()