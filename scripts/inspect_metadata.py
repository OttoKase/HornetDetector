import csv

METADATA_FILE = "data/metadata/hornets_metadata.csv"

def inspect_metadata():
    """Inspect the structure and content of the metadata file."""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        # Print all column headers
        print("Column headers:")
        print(reader.fieldnames)
        print("\n" + "="*50 + "\n")
        
        # Print first 3 records with all fields
        for idx, row in enumerate(reader):
            if idx < 3:
                print(f"Record {idx + 1}:")
                for key, value in row.items():
                    if value.strip():  # Only print non-empty fields
                        print(f"  {key}: {value[:100]}")  # Truncate long values
                print()
            else:
                break

if __name__ == "__main__":
    inspect_metadata()