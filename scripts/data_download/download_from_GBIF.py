import os
import csv
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Configuration
BUG_TYPE = os.getenv("BUG_TYPE")
OUTPUT_DIR = f"data/{BUG_TYPE}"
METADATA_FILE = f"data/metadata/{BUG_TYPE}_metadata.csv"

# License types to allow (permissive and non-commercial licenses)
# These are URL patterns from license URLs
ALLOWED_LICENSES = {
    "cc0",
    "by/4.0",
    "by/3.0",
    "by/2.5",
    "by/2.0",
    "by-sa/4.0",
    "by-sa/3.0",
    "by-sa/2.5",
    "by-nc/4.0",
    "by-nc/3.0",
    "by-nc/2.5",
    "by-nc-sa/4.0",
    "by-nc-sa/3.0",
    "by-nc-sa/2.5",
}

def create_output_directory():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

def load_metadata(csv_file):
    """Load metadata from GBIF Darwin Core CSV file."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        print("Please export a Darwin Core archive from GBIF and extract it.")
        return []
    
    records = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        # GBIF uses tab-separated values
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            records.append(row)
    
    print(f"Loaded {len(records)} records from metadata")
    return records

def filter_by_license(records):
    """Filter records to only include permissive licenses."""
    filtered = []
    for record in records:
        license_url = record.get('license', '').lower()
        # Check if license URL contains any allowed license pattern
        is_allowed = any(pattern in license_url for pattern in ALLOWED_LICENSES)
        if is_allowed or license_url == '':
            filtered.append(record)
    
    print(f"Filtered to {len(filtered)} records with permissive licenses")
    return filtered

def get_image_url(record):
    """Extract image URL from record."""
    # GBIF stores image URLs in the 'identifier' field for multimedia
    url = record.get('identifier', '').strip()
    return url

def download_image(url, filename, max_retries=3):
    """Download a single image with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"Failed to download {url}: {e}")
                return False
    return False

def main():
    print("GBIF Hornet Image Downloader")
    print("=" * 50)
    
    # Create output directory
    create_output_directory()
    
    # Load metadata
    records = load_metadata(METADATA_FILE)
    if not records:
        return
    
    # Filter by license
    records = filter_by_license(records)
    
    # Download images
    successful = 0
    failed = 0
    skipped = 0
    
    for idx, record in enumerate(records, 1):
        url = get_image_url(record)
        
        if not url:
            skipped += 1
            continue
        
        # Generate filename
        filename = f"{OUTPUT_DIR}/hornet_{idx:05d}.jpg"
        
        # Skip if already exists
        if os.path.exists(filename):
            skipped += 1
            continue
        
        print(f"[{idx}/{len(records)}] Downloading: {url[:60]}...")
        
        if download_image(url, filename):
            successful += 1
        else:
            failed += 1
        
        # Rate limiting - be respectful to GBIF servers
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"Download complete!")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped (no URL or already exists): {skipped}")
    print(f"Images saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()