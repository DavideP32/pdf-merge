from core import validate_and_correct_output_file_name, create_directory, sort_files, merge_pdf, MergeError, WrongFileNameError
from pathlib import Path
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox

class MergeApp:
    """
        We create a class to encapsulate the GUI elements and the logic. 
        This prevents the need for global variables to pass from one method to another, since in the 'command='
        part, we cannot specify anything in the argument of the called function. 

        The __init__ is a constructor. When we create an object of this class, we build the interface. 

        The 'self' keyword is always needed for all the methods and represents the variable for a specific
        instance of the object (OPPOSITE of 'static' in java). If we need to create a static variable, we
        declare a normal variable out of the constructor. 

        note that: self.select_folder is equal to select_folder(self)
    """
    def __init__(self, window):
        self.window = window
        self.path_input_files = None
        self.output_file_name_var = tk.StringVar()
        self.input_folder_name_var = tk.StringVar()
        self.checkbox_outline = tk.BooleanVar()
        self.output_folder_name = "merged"

        # Button to select folder with pdfs
        button_select_folder = tk.Button(window, text="Select Folder", command=self.select_folder, font=('calibre',10,'normal'))
        button_select_folder.pack(pady=10)

        #  Entry readonly to print the selected folder
        text_input_folder = tk.Entry(window, textvariable=self.input_folder_name_var, width=100, font=('calibre',10,'normal'))
        text_input_folder.pack(pady=5)
        text_input_folder.config(state='readonly')

        # Entry for writing the name of the file
        text_output_file = tk.Entry(window, textvariable=self.output_file_name_var, font=('calibre',10,'normal'))
        text_output_file.pack(pady=5)

        # Checkbox to enable/disable outline
        checkbutton = tk.Checkbutton(window, text="Create Outline", variable=self.checkbox_outline, 
                                onvalue=True, offvalue=False, font=('calibre',10,'normal'))
        checkbutton.pack(pady=5)

        # Final OK button to merge
        ok_button = tk.Button(window, text="OK", command=self.run_merge)
        ok_button.pack(pady=10)


    def select_folder(self):
        folder_path = fd.askdirectory(title="Select Folder")

        if folder_path:
            self.path_input_files = Path(folder_path)
            self.input_folder_name_var.set(folder_path) # write the folder path in the readonly entry
            print(f"Selected folder: {self.path_input_files}")


    def run_merge(self):
        """
            Since the main() should not run functions in the loop, all the logic and execution should be put in this
            function, which is triggered by the 'OK' button at the end of the form, once all the data has been filled. 
            Here we call the core.py functions which are used to merge the PDFs.
        """

        if self.path_input_files is None:
            messagebox.showerror("Error", "Select a folder first.")
            return

        if not self.path_input_files.is_dir():
            messagebox.showerror("Error", "The specified folder does not exist or is not a directory.")
            return

        if not self.output_file_name_var.get().strip():
            messagebox.showerror("Error", "Please enter a name for the output file.")
            return

        output_file_name = self.output_file_name_var.get().strip()

        try:
            output_file_name = validate_and_correct_output_file_name(output_file_name)
        except WrongFileNameError as e:
            messagebox.showerror("Error", f"Error with the file name: {e}")
            return

        is_outline = self.checkbox_outline.get()
        
        output_path = create_directory(path_input_files=self.path_input_files, output_folder_name=self.output_folder_name)
        

        list_of_files = list(self.path_input_files.glob('*.pdf'))
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

    window = tk.Tk()
    window.geometry("1000x600")
    window.title("Pdf Toolkit")
    MergeApp(window)

    # The loop
    window.mainloop()


if __name__ == "__main__":
    main()