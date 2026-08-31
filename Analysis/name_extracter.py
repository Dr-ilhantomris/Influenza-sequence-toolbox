import os  
from Bio import SeqIO

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

