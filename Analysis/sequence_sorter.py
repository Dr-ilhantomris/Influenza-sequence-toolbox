import os
from Bio import SeqIO

from Analysis.metadata_config import parse_header_metadata

class InfluenzaSegmentSorter:
    # defining strict source of truth 
    VALID_INFLUENZA_SEGMENTS = {"HA", "NA", "MP", "NS", "NP", "PA", "PB1", "PB2"}

    def __init__(self, fasta_path, output_dir, target_segments, chosen_columns):
        self.fasta_path = fasta_path
        self.output_dir = output_dir
        self.chosen_columns = chosen_columns

        # 1. Clean up user inputs
        cleaned_inputs = {seg.strip().upper() for seg in target_segments if seg.strip()}

        # 2. Filter input against a strict library of valid segments
        self.target_segments = cleaned_inputs.intersection(self.VALID_INFLUENZA_SEGMENTS)
       
        # Find any invalid entries the user typed to show a helpful warning
        invalid_entries = cleaned_inputs - self.VALID_INFLUENZA_SEGMENTS
        if invalid_entries:
            print(f"[!] Warning: Ignoring invalid segment entries: {', '.join(invalid_entries)}")

        # 3. Critical guard: crash or stop immediately if NO valid genes
        if not self.target_segments:
            raise ValueError(
                f"Aborting process! None of your entered segments match the valid list:\n"
                f"Valid choices are: {', '.join(sorted(self.VALID_INFLUENZA_SEGMENTS))}"
            )

    def sort_sequences(self):
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Get base filename of the input fasta
        file_base, ext = os.path.splitext(os.path.basename(self.fasta_path))

        print(f"\n⚡ Processing valid segments in a single pass: {', '.join(self.target_segments)}")

        file_handles = {}
        counts = {}

        try:
            # Initialize files and headers Only for the validated targets
            for segment in self.target_segments:
                csv_path = os.path.join(self.output_dir, f"{file_base}_{segment}_subset.csv")
                file_handles[segment] = open(csv_path, "w")

                # Header row generated completely dynamically 
                headers = ["Number"] + self.chosen_columns
                file_handles[segment].write(",".join(headers) + "\n")
                counts[segment] = 0

            # Read through sequence in a single memory-efficient pass
            total_scanned = 0
            for record in SeqIO.parse(self.fasta_path, "fasta"):
                total_scanned += 1
                header_parts = record.id.split('|')

                # Loop through each item in the header chunks dynamically 
                for header_position in header_parts:
                    # Clean the curent chunk
                    current_chunk = header_position.strip()

                    if current_chunk in self.target_segments:
                        current_segment = current_chunk

                        counts[current_segment] += 1

                        row_cells = parse_header_metadata(record, self.chosen_columns)

                        safe_row = [f'"{val}"' if not str(val).isdigit() else str(val) for val in row_cells]
                        
                        file_handles[current_segment].write(
                            f"{counts[current_segment]}," + ",".join(safe_row) + "\n"
                        )

                        break

            print(f"\nScan complete. Total sequences scanned: {total_scanned:,}")
            print("📊 Extracted Row Breakdown:")
            for segment, cnt in counts.items():
                print(f" - {segment}: {cnt:,} sequences saved")

        finally:
            # Securely close all file handles to prevent data corruption
            for handle in file_handles.values():
                handle.close()
            print(f"\nAll valid files saved successfully inside: {self.output_dir}")