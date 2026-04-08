import os
import uuid
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploaded_media"

def save_upload_file(upload_file: UploadFile) -> str:
    """Saves an UploadFile to the local disk and returns the relative URL path."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    # Extract extension
    _, ext = os.path.splitext(upload_file.filename)
    if not ext:
        ext = ".bin" # fallback
        
    random_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, random_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return f"/media/{random_filename}"
