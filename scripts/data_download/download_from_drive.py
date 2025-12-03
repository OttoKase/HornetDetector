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
                fields="nextPageToken, files(id, name, mimeType)",
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
        
def process_folder(service, folder_id, current_output_dir, downloaded_ids):
    # 1. List contents of the current folder
    current_files = list_all_files(service, folder_id) # The existing function
    
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
            process_folder(service, item_id, new_output_dir, downloaded_ids)
            
        elif item_id not in downloaded_ids:
            # --- Found a File (DOWNLOAD) ---
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
    # This history set will be passed around and updated by the process_folder function
    downloaded_ids = load_history()
    
    print(f"💾 Loaded {len(downloaded_ids)} files from history.")
    
    # 3. START RECURSIVE PROCESSING
    # Call process_folder with the root folder ID and the main output directory.
    try:
        process_folder(
            service=service, 
            folder_id=DRIVE_FOLDER_ID,       # The ID of the Google Drive folder you want to download
            current_output_dir=OUTPUT_DIR, # The root directory on your local machine
            downloaded_ids=downloaded_ids
        )
        
        print("\n🎉 All folders processed. Download complete!")
    except KeyboardInterrupt:
        print("\n\n⛔ Full download process interrupted. Final progress saved.")    

if __name__ == '__main__':
    main()