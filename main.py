import os
import subprocess
import tkinter as tk
from tkinter import filedialog

# Import your modules from the analysis folder
from Analysis.name_extracter import FASTANameExtractor
from Analysis.sequence_sorter import InfluenzaSegmentSorter
from Analysis.metadata_config import prompt_column_selection, prompt_qc_thresholds

def get_project_paths():
    # Calculates all relative workspace locations dynamically
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if a 'data' folder exists inside the root; if so, default to it
    default_input_dir = os.path.join(current_dir, "data")
    if not os.path.exists(default_input_dir):
            default_input_dir = current_dir

    # Determine the default folder for saving the output
    default_output_dir = os.path.join(current_dir, "output")
    if not os.path.exists(default_output_dir):
                os.makedirs(default_output_dir)

    return default_input_dir, default_output_dir

def run_name_extractor(default_input, default_output, chosen_columns):
    # Handles GUI pickers and executes the Name Extractor Module
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    print("\n[1] Running Name Extractor...")
    fasta_input = filedialog.askopenfilename(
        title="Select Input FASTA File",
        initialdir=default_input, # Defaults Finder directly to your project folder
        filetypes=[("FASTA files", "*.fasta *.fa *.fna *.faa"), ("All files", "*.*")]  
    )

    # If the user closes the window or hits cancel, stop execution safely
    if not fasta_input:
        print("Operation cancelled: No input file selected")
        return

    # Strip the .fasta extension from the input path and give suggested filename
    file_base, ext = os.path.splitext(fasta_input)
    suggested_filename = f"{os.path.basename(file_base)}_output.csv"

    # Open the save window with your dynamic suggestion pre-filled
    csv_output = filedialog.asksaveasfilename(
        title="Save Sequence Names CSV As",
        initialdir= default_output, 
        initialfile=suggested_filename, # Dynamically fills in based on input
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if csv_output:
        # Run the extractor directly
        extractor = FASTANameExtractor(fasta_input, csv_output, chosen_columns)
        extractor.extract_names_to_csv()

        # Automatically open the generated file using your Mac's default viewer
        print(f"Opening {csv_output}")
        subprocess.call(["open", csv_output])

def run_segment_sorter(default_input, default_output, chosen_columns, qc_filters):
    # Handles user choices to extract all, one, or manually specified gene segments.
    print("\n" + "-"*40)
    print("🧬 GENE SEGMENT FILTER OPTIONS 🧬")
    print("-"*40)
    print("1. Process ALL 8 standard genes into separate files")
    print("2. Process a SINGLE specific gene segment (e.g., HA)")
    print("3. MANUAL ENTRY: Type specific genes to sort (e.g., HA, NA, NS)")
    print("4. Back to Main Menu")

    sub_choice = input("Select an option (1-4): ").strip()
    if sub_choice == "4" or sub_choice not in ["1", "2", "3"]:
         return

    target_list = []
    if sub_choice == "1":
         target_list = list(InfluenzaSegmentSorter.VALID_INFLUENZA_SEGMENTS)
    elif sub_choice == "2":
         target_list = [input("Type the single segment name: ").strip().upper()]
    elif sub_choice == "3":
         print("\nAvailable options: HA, NA, MP, NS, NP, PA, PB1, PB2")
         raw_input = input("Enter desired genes separated by commas (e.g., HA, NA): ")
         target_list = [gene.strip().upper() for gene in raw_input.split(",") if gene.strip()]

    # Assess whether manual input segment is listed 
    target_set = set(target_list)
    target_list_valid = target_set.intersection(InfluenzaSegmentSorter.VALID_INFLUENZA_SEGMENTS)
         
    if not target_list_valid:
        print("Operation cancelled: No genes specified.")
        return

    # Initialize standard Tkinter hidden frame
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    
    print("\nPlease select your input FASTA file...")
    fasta_input = filedialog.askopenfilename(
        title="Select FASTA File to Filter",
        initialdir=default_input,
        filetypes=[("FASTA files", "*.fasta *.fa *.fna *.faa"), ("All files", "*.*")]
    )
    if not fasta_input: 
        print("Operation cancelled: No file chosen.")
        return

    try: 
        sorter = InfluenzaSegmentSorter(fasta_input, default_output, target_list, chosen_columns, qc_filters)
        sorter.sort_sequences()

        print(f"Opening output folder: {default_output}")
        subprocess.call(["open", default_output])

    except ValueError as e:
        print(f"\n[❌ ERROR] {e}")

def main():
      default_input, default_output = get_project_paths()

      # Query configuration settings ONCE upfront when program mounts
      chosen_columns = prompt_column_selection()

      # No QC filtering active until the user explicitly configures thresholds
      qc_filters = None

      while True:
        print("\n" + "="*40)
        print("🧬 SEQUENCE ALIGNMENT TOOLBOX 🧬")
        print("="*40)
        print(f"Active Columns: {', '.join(chosen_columns)}")
        if qc_filters:
             print(f"Active QC Filters: min={qc_filters['min_bp']}bp, "
                   f"max={qc_filters['max_bp']}bp, "
                   f"max_N={qc_filters['max_n_pct'] * 100:.1f}%")
        else:
             print("Active QC filters: None")
        print("1. Extract Sequence Names to CSV (Excel)")
        print("2. Sort / Filter Sequence Names (Next Task)")
        print("3. Change Global Column Layout Settings")
        print("4. Configure Quality Control (QC) Filters")
        print("5. Exit Program")
        print("-"*40) 

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
              run_name_extractor(default_input, default_output, chosen_columns)
        elif choice == "2":
              run_segment_sorter(default_input, default_output, chosen_columns, qc_filters)
        elif choice == "3":
            # Reprompts column layout selections dynamically on request
            chosen_columns = prompt_column_selection()
        elif choice == "4":
             # Reprompts QC threshold selections dynamically on request
             qc_filters = prompt_qc_thresholds()
        elif choice == "5":
            print("\nExiting program. Meow Meowwww")
            break
        else:
            print("\nInvalid choice. Please pick a number from 1 to 5.")

if __name__ == "__main__":
    main()