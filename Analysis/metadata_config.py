# Analysis/metadata_config.py

# Complete vocabulary of what can be extracted from a standard line
COLUMNS_MAP = {
    "1": {"label": "Full_ID", "description": "The raw unbroken header string"},
    "2": {"label": "Collection_Date", "description": "The date field from the header"},
    "3": {"label": "Segment", "description": "The gene segment name"},
    "4": {"label": "Accession_ID", "description": "The database unique identifier number"},
    "5": {"label": "Subtype", "description": "The HxNx influenza variant type"},
    "6": {"label": "Sequence_Length", "description": "The nucleotide count of the sequence"},
    "7": {
        "label": "Isolate_Name", 
        "description": "The unique historical identifier",
        "custom_attributes": {}  # Put unknown incoming keys here later (e.g. host, location, etc.)
    },
    "8": {"label": "N_percentage", "description": "Missing data count percentage (N characters)"},
    "9": {"label": "GC_Content", "description": "GC content percentage"},
    "10": {"label": "Sequence", "description": "WARNING: Raw nucleotide sequence string causes large file sizes"}
}

def prompt_column_selection():
    # Prompts the user to select which columns to export globally 
    print("\n" + "-"*50)
    print("📊 METADATA COLUMN EXPORT SELECTION 📊")
    print("-"*50)
    print("Select which metrics you want displayed in your output sheets.")
    print("Type the numbers separated by commas (e.g., 2,3,7,9)")
    print("Leave blank and press Enter to select standard metadata columns (1-9).")
    print("-"*50)

    for key, info in COLUMNS_MAP.items():
        print(f"[{key:>2}] {info['label']:<17} -> {info['description']}")
    print("-"*50)

    user_input = input("Enter your choices: ").strip()

    # Critical: if blank, default to options 1 through 9, only skipping 10 due to its size in massive FASTAs
    if not user_input:
        default_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return [COLUMNS_MAP[k]["label"] for k in default_keys]

    chosen_keys = [k.strip() for k in user_input.split(",") if k.strip() in COLUMNS_MAP]

    if not chosen_keys:
        print("[!] No valid choices entered. Defaulting to standard columns (1-9).")
        default_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return [COLUMNS_MAP[k]["label"] for k in default_keys]

    # Return the exact array of label strings chose by the user
    return [COLUMNS_MAP[k]["label"] for k in chosen_keys]

def prompt_qc_thresholds():
    # Collects quality filtering constraints from the user text menu
    print("\n" + "-"*50)
    print("🧪 QUALITY CONTROL FILTER CONFIGURATION 🧪")
    print("-"*50)
    print("Set your constraints. Press Enter on any option to skip/ignore it.")
    print("-"*50)

    # Minimum length filter
    raw_min = input("Minimum sequence length in base pairs (e.g., 1000): ").strip()
    min_bp = int(raw_min) if raw_min.isdigit() else 0

    # Maximum length filter
    raw_max = input("Maximum sequence length in base pairs (e.g., 2000): ").strip()
    max_bp = int(raw_max) if raw_max.isdigit() else float('inf')

    # Ambiguity filter
    raw_n_pct = input("Maximum allowed ambiguous 'N' characters in  ")
    max_n_pct = float(raw_n_pct) / 100.0 if raw_n_pct else float('inf') 

    return {"max_n_pct": max_n_pct, "min_bp": min_bp, "max_bp": max_bp}
    
def parse_header_metadata(record, chosen_columns, qc_filters=None):

    # General parsing function that breaks a record header apart and maps it dynamically to your requested column settings
    header_parts = record.id.split('|')
    while len(header_parts) < 5:
        header_parts.append("")

    # Real-time computation of raw molecular attributes
    seq_str = str(record.seq).upper()
    seq_len = len(seq_str)
    n_count = seq_str.count('N')

    # Calculate real-time ambiguity percentage safely
    current_n_pct = (n_count / seq_len) if seq_len > 0 else 0.0

    # Quality threshold validation block
    if qc_filters:
        if current_n_pct > qc_filters["max_n_pct"]:
            return None # Fails ambiguity percentage limit test
        if seq_len < qc_filters["min_bp"] or seq_len > qc_filters["max_bp"]:
            return None # Fails size range check
    
    # Calcualte compostition statistics
    g_count = seq_str.count('G')
    c_count = seq_str.count('C')
    gc_percentage = ((g_count + c_count) / seq_len * 100) if seq_len > 0 else 0.0

    n_pct_display = f"{(current_n_pct * 100):.2f}%"

    # Gather data mappings matching the exact labels inside your COLUMNS_MAP definitions
    data_source = {
        "Full_ID": record.id,
        "Collection_Date": header_parts[1].strip(),
        "Segment": header_parts[2].strip().upper(),
        "Accession_ID": header_parts[3].strip(),
        "Subtype": header_parts[4].strip().upper(),
        "Sequence_Length": str(seq_len),
        "Isolate_Name": header_parts[0].strip(),
        "N_percentage": f"{n_count} ({n_pct_display})",
        "GC_Content": f"{gc_percentage:.2f}%",
        "Sequence": seq_str  # Handles mapping the full string on demand
    }

    # Return only the cell columns specified by the global checklist selection layout
    return [data_source[col] for col in chosen_columns]