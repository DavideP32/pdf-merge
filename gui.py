from core import validate_output_file_name, create_directory, sort_files, merge_pdf, MergeError, WrongFileNameError
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog as sd
from tkinter import filedialog as fd
from tkinter import messagebox
import sys


def select_folder():
    global path_input_files
    folder_path = fd.askdirectory(title="Select Folder")

    if folder_path:
        path_input_files = Path(folder_path)
        input_folder_name_var.set(folder_path)
        print(f"Selected folder: {path_input_files}")


def run_merge():
    """
        Since the main() should not run functions in the loop, all the logic and execution should be put in this
        function, which is triggered by the 'OK' button at the end of the form, once all the data has been filled. 
        Here we call the core.py functions which are used to merge the PDFs.
    """
    output_folder_name = "merged"

    if path_input_files is None:
        messagebox.showerror("Error", "Select a folder first.")
        return

    output_file_name = output_file_name_var.get().strip()

    try:
        validate_output_file_name(output_file_name)
    except WrongFileNameError as e:
        messagebox.showerror("Error", f"Error with the file name: {e}")
        return


    if not output_file_name.endswith(".pdf"):
        output_file_name += ".pdf"

    is_outline = checkbox_outline.get()

    if not path_input_files.is_dir():
        messagebox.showerror("Error", "The specified folder does not exist or is not a directory.")
        return
    output_path = create_directory(path_input_files=path_input_files, output_folder_name=output_folder_name)
    

    list_of_files = list(path_input_files.glob('*.pdf'))
    if not list_of_files:
        messagebox.showerror("Error", "No PDF file is present in the given folder.")
        return
    print(f"Found PDF files: {list_of_files}")
    
    sorted_files = sort_files(list_of_files=list_of_files)

    try:
        merge_pdf(sorted_files=sorted_files, 
                    is_create_outline=is_outline,
                    output_path=output_path, 
                    output_file_name=output_file_name)
        messagebox.showinfo("Success", f"Merged PDF created successfully at: {output_path / output_file_name}")
    except MergeError as e:
        messagebox.showerror("Error", f"Error reading PDF file: {e}")
        return


def main():
    """
        # --------------------------------- GUI SETUP -------------------------------- #
        In the main() function we define the visual interface (like an html form) to interact with the user.
        The GUI runs in a LOOP, waiting for EVENTS. 
        For this reason, there should not be any function in main(), since it would run over and over again. 
        We should use event-driven programming instead (click button -> execute)
    """

    global path_input_files
    global output_file_name_var
    global input_folder_name_var
    global checkbox_outline


    window = tk.Tk()
    window.geometry("1000x600")
    window.title("Pdf Toolkit")
    
    # Button to select folder with pdfs
    path_input_files = None
    button_select_folder = tk.Button(window, text="Select Folder", command=select_folder, font=('calibre',10,'normal'))
    button_select_folder.pack(pady=10)

    #  Entry readonly to print the selected folder
    input_folder_name_var = tk.StringVar()
    text_input_folder = tk.Entry(window, textvariable=input_folder_name_var, width=100, font=('calibre',10,'normal'))
    text_input_folder.pack(pady=5)
    text_input_folder.config(state='readonly')

    # Entry for writing the name of the file
    output_file_name_var=tk.StringVar()
    text_output_file = tk.Entry(window, textvariable=output_file_name_var, font=('calibre',10,'normal'))
    text_output_file.pack(pady=5)

    # Checkbox to enable/disable outline
    checkbox_outline = tk.BooleanVar()
    checkbutton = tk.Checkbutton(window, text="Create Outline", variable=checkbox_outline, 
                             onvalue=True, offvalue=False, font=('calibre',10,'normal'))
    checkbutton.pack(pady=5)

    # Final OK button to merge
    ok_button = tk.Button(window, text="OK", command=run_merge)
    ok_button.pack(pady=10)

    # The loop
    window.mainloop()


if __name__ == "__main__":
    main()