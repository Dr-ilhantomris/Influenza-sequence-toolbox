import os
# import subprocess  
from Bio import SeqIO
# import tkinter as tk
# from tkinter import filedialog

from Analysis.metadata_config import parse_header_metadata

class FASTANameExtractor:
    def __init__(self, fasta_path, output_csv_path, chosen_columns):
        self.fasta_path = fasta_path
        self.output_csv_path = output_csv_path
        self.chosen_columns = chosen_columns

    def extract_names_to_csv(self):
        print(f"Parsing {self.fasta_path}...")
        os.makedirs(os.path.dirname(self.output_csv_path), exist_ok=True)

        count = 0
        with open(self.output_csv_path, "w") as csv_file:
            # Create dynamic spreadsheet header columns using your options list
            headers = ["Number"] + self.chosen_columns
            csv_file.write(",".join(headers) + "\n")

            # SeqIO.parse streams the file line-by-line 
            for record in SeqIO.parse(self.fasta_path, "fasta"):
                count += 1

                # INITIALIZE IT HERE: Catch the array returned from metadata_config.py
                row_cells = parse_header_metadata(record, self.chosen_columns)

                # Sanitize text elements with quotes so commans within names won't break columns
                safe_row = [f'"{val}"' if not str(val).isdigit() else str(val) for val in row_cells]

                # Write rows separated by commas for Excel columns
                csv_file.write(f"{count}," + ",".join(safe_row) + "\n")
                

        print(f"Success! Extracted {count:,} sequence names to: {self.output_csv_path}")

# Direct execution
'''
if __name__ == "__main__":
    # Initialize a hidden Tkinter root window
    root = tk.Tk()
    root.withdraw()

    # Force the file picker windows to come to the front of your screen
    root.wm_attributes('-topmost', 1)

    # 0A. Get the folder where this script lives
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    # 0B. Go up one level to get your project root directory
    project_root = os.path.dirname(current_dir)

    # Check if a 'data' folder exists inside the root; if so, default to it
    default_input_dir = os.path.join(project_root, "data")
    if not os.path.exists(default_input_dir):
        default_input_dir = project_root

    print("Please select your input FASTA file in the pop-up window...")

    # 1. Open the native macOS Finder window to select the input FASTA file
    fasta_input = filedialog.askopenfilename(
        title="Select Input FASTA File",
        initialdir=default_input_dir, # Defaults Finder directly to your project folder
        filetypes=[("FASTA files", "*.fasta *.fa *.fna *.faa"), ("All files", "*.*")]
    )

    # If the user closes the window or hits cancel, stop execution safely
    if not fasta_input:
        print("Operation cancelled: No input file selected")

    else:
        print(f"Selected Input: {fasta_input}")
        print("Please choose where to save the output CSV spreadsheet...")

        # 2. Open the window to select the destination folder and name the output file
        # We pre-fill the name as "{fasta_input}_output.csv"
        
        # 2A. strip the .fasta extension from the input path
        file_base, ext = os.path.splitext(fasta_input)

        # 2B. Extract just the filename to pre-fill the dialog box
        suggested_filename = f"{os.path.basename(file_base)}_output.csv"

        # Determine the default folder for saving the output
        default_output_dir = os.path.join(project_root, "output")
        if not os.path.exists(default_output_dir):
            os.makedirs(default_output_dir)

        # 2C Open the save window with your dynamic suggestion pre-filled
        csv_output = filedialog.asksaveasfilename(
            title="Save Sequence Names CSV As",
            initialdir= default_output_dir, 
            initialfile=suggested_filename, # Dynamically fills in based on input
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not csv_output:
            print("Operation cancelled: No output location selected")
        else:
            # Run the extractor directly
            extractor = FASTANameExtractor(fasta_input, csv_output)
            extractor.extract_names_to_csv()

            # Automatically open the generated file using your macs default viewer
            print(f"Opening {csv_output}")
            subprocess.call(["open", csv_output])
'''