import json
import io
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()
DRIVE_FOLDER_CODE = os.getenv("DRIVE_FOLDER_CODE")
CREDENTIALS_FILE = "credentials.json"
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

if (DRIVE_FOLDER_CODE == "roboflow"):
    OUTPUT_DIR = "data/images/drive/roboflow"
    HISTORY_FILE = "data/images/drive/roboflow/.download_progress.json"
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ROBOFLOW")
    
elif (DRIVE_FOLDER_CODE == "top-down"):
    OUTPUT_DIR = "data/images/drive/top-down"
    HISTORY_FILE = "data/images/drive/top-down/.download_progress.json"
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_TOP-DOWN")
    
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

def get_authenticated_service():
    """Authenticates using the Service Account JSON."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Could not find {CREDENTIALS_FILE}. Did you generate it?")
    
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)

def list_all_files(service, folder_id):
    """Lists ALL files in the folder, handling the 50-file page limit automatically."""
    print(f"📋 Fetching file list from Drive (this might take a moment)...")
    files = []
    page_token = None
    
    while True:
        try:
            results = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageSize=1000, # Request up to 1000 at a time
                pageToken=page_token,
                orderBy='folder,name'
            ).execute()
            
            items = results.get('files', [])
            files.extend(items)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            print(f"Error listing files: {e}")
            break
            
    print(f"✅ Found {len(files)} total files in the cloud.")
    return files

def download_file(service, file_id, file_name, destination_path):
    """Downloads a single file using the Google API."""
    request = service.files().get_media(fileId=file_id)
    
    with io.FileIO(destination_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # You can print percentage here if you want:
            # print(f"Download {int(status.progress() * 100)}%.", end='\r')

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_history(history_set):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(list(history_set), f)
        
def get_empty_label_files(service, labels_folder_id):
    """Scan labels folder and return set of filenames (without extension) that are empty."""
    print("\n🔍 Scanning labels folder for empty files...")
    labels_files = list_all_files(service, labels_folder_id)
    
    empty_labels = set()
    
    for label_file in labels_files:
        if label_file['mimeType'] != FOLDER_MIME_TYPE:
            file_size = int(label_file.get('size', 0))
            filename_base = label_file['name'].rsplit('.', 1)[0]  # Remove extension
            
            if file_size == 0:
                empty_labels.add(filename_base)
                print(f"  ❌ Empty label: {label_file['name']}")
            else:
                print(f"  ✅ Valid label: {label_file['name']} ({file_size} bytes)")
    
    print(f"Found {len(empty_labels)} empty label files\n")
    return empty_labels

def find_folder_by_name(service, parent_folder_id, folder_name):
    """Find a folder by name within a parent folder."""
    results = service.files().list(
        q=f"'{parent_folder_id}' in parents and trashed=false and mimeType='{FOLDER_MIME_TYPE}' and name='{folder_name}'",
        fields="files(id, name)",
        pageSize=1
    ).execute()
    
    items = results.get('files', [])
    if items:
        return items[0]['id']
    return None
        
def process_folder(service, folder_id, current_output_dir, downloaded_ids, empty_labels=None):
    """Recursively process folders and download files, skipping images with empty labels."""
    if empty_labels is None:
        empty_labels = set()
    
    # 1. List contents of the current folder
    current_files = list_all_files(service, folder_id)
    
    # 2. Iterate through contents
    for index, file_info in enumerate(current_files):
        item_id = file_info['id']
        item_name = file_info['name']
        item_mime = file_info['mimeType']

        if item_mime == FOLDER_MIME_TYPE:
            # --- Found a Folder (RECURSION) ---
            new_output_dir = os.path.join(current_output_dir, item_name)
            os.makedirs(new_output_dir, exist_ok=True)
            
            # CALL ITSELF to process the subfolder
            process_folder(service, item_id, new_output_dir, downloaded_ids, empty_labels)
            
        elif item_id not in downloaded_ids:
            # --- Found a File (CHECK AND DOWNLOAD) ---
            # Get filename without extension
            filename_base = item_name.rsplit('.', 1)[0]
            
            # Check if this image has an empty label
            if filename_base in empty_labels:
                print(f"[{index + 1}/{len(current_files)}] ⏭️  Skipping {item_name} (empty label)")
                downloaded_ids.add(item_id)
                save_history(downloaded_ids)
                continue
            
            save_path = os.path.join(current_output_dir, item_name)
            print(f"[{index + 1}/{len(current_files)}] Downloading {item_name}...", end="", flush=True)
            
            try:
                download_file(service, item_id, item_name, save_path)
                
                # Update history immediately
                downloaded_ids.add(item_id)
                save_history(downloaded_ids)
                print(" Done ✅")
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f" ❌ Error: {e}")

def main():
    # 1. Login
    service = get_authenticated_service()
    
    # 2. Load History ONCE
    downloaded_ids = load_history()
    print(f"💾 Loaded {len(downloaded_ids)} files from history.")
    empty_labels = None
    
    if (DRIVE_FOLDER_CODE == "roboflow"):
        # 3. Find 'images' and 'labels' folders within root
        print(f"\n🔎 Looking for 'images' and 'labels' folders...")
        labels_folder_id = find_folder_by_name(service, DRIVE_FOLDER_ID, "labels")
        images_folder_id = find_folder_by_name(service, DRIVE_FOLDER_ID, "images")
        
        if not labels_folder_id or not images_folder_id:
            print("❌ Could not find 'images' and/or 'labels' folders!")
            return
        
        print(f"✅ Found both folders\n")
        
        # 4. Scan labels folder first to identify empty labels
        empty_labels = get_empty_label_files(service, labels_folder_id)
    
    # 5. START RECURSIVE PROCESSING for images
    # Pass empty_labels to process_folder so it knows which to skip
    try:
        images_output = os.path.join(OUTPUT_DIR, 'images')
        os.makedirs(images_output, exist_ok=True)
        
        print("📥 Starting image download...\n")
        process_folder(
            service=service, 
            folder_id=images_folder_id,
            current_output_dir=images_output,
            downloaded_ids=downloaded_ids,
            empty_labels=empty_labels
        )
        
        print("\n🎉 All files processed. Download complete!")
    except KeyboardInterrupt:
        print("\n\n⛔ Download process interrupted. Final progress saved.")     

if __name__ == '__main__':
    main()