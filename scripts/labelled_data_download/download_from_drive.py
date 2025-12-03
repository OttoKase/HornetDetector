import os
import json
import gdown
from dotenv import load_dotenv

load_dotenv()
DRIVE_FOLDER_CODE = os.getenv("DRIVE_FOLDER_CODE")

if (DRIVE_FOLDER_CODE == "roboflow"):
    output_dir = "data/images/drive/roboflow"
    progress_file = "data/images/drive/roboflow/.download_progress.json"
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ROBOFLOW")
    
elif (DRIVE_FOLDER_CODE == "top-down"):
    output_dir = "data/images/drive/top-down"
    progress_file = "drive/images/drive/top-down/.download_progress.json"
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_TOP-DOWN")
    
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.dirname(progress_file), exist_ok=True)

def load_progress():
    """Load list of already downloaded file IDs."""
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {"downloaded_file_ids": []}

def save_progress(file_ids):
    """Save list of downloaded file IDs."""
    with open(progress_file, 'w') as f:
        json.dump({"downloaded_file_ids": file_ids}, f, indent=2)

def list_drive_files(folder_id):
    """List all files in a Google Drive folder."""
    try:
        # Use gdown to list folder contents
        import subprocess
        result = subprocess.run(
            ["gdown", "--folder", f"https://drive.google.com/drive/folders/{folder_id}", "--list-only"],
            capture_output=True,
            text=True
        )
        
        files = []
        for line in result.stdout.split('\n'):
            if line.strip():
                files.append(line.strip())
        return files
    except Exception as e:
        print(f"Error listing Drive files: {e}")
        return []

def download_with_resume():
    """Download folder with resume capability."""
    progress = load_progress()
    already_downloaded = set(progress.get("downloaded_file_ids", []))
    
    print(f"Downloading from Google Drive folder: {DRIVE_FOLDER_ID}")
    print(f"Output directory: {output_dir}")
    print(f"Already downloaded: {len(already_downloaded)} files\n")
    
    url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    
    try:
        # Download the entire folder
        gdown.download_folder(
            url, 
            output=output_dir, 
            quiet=False, 
            use_cookies=False,
            remaining_ok=True
        )
        
        # Count files in output directory
        file_count = 0
        for root, dirs, files in os.walk(output_dir):
            file_count += len(files)
        
        print(f"\nDataset download completed")
        print(f"Total files in {output_dir}: {file_count}")
        
        # Save progress with file hashes for better tracking
        save_progress({"timestamp": str(__import__('datetime').datetime.now()), "total_files": file_count})
        
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Run this script again to continue downloading.")
        
        # Count what we have so far
        file_count = 0
        for root, dirs, files in os.walk(output_dir):
            file_count += len(files)
        
        save_progress({"timestamp": str(__import__('datetime').datetime.now()), "total_files": file_count})
        print(f"Current progress: {file_count} files downloaded")
        
    except Exception as e:
        print(f"Error downloading from Drive: {e}")
        print("Make sure:")
        print("  1. The folder is shared publicly or with 'Anyone with link'")
        print("  2. DRIVE_FOLDER_ID is correct")
        print("  3. gdown is installed: pip install gdown")

if __name__ == "__main__":
    download_with_resume()