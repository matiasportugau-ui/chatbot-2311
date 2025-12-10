
import os
import dropbox
import time
import uuid
import re
import json
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DROPBOX_API_KEY = os.getenv("DROPBOX_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot-context")

# Initialize clients
dbx = dropbox.Dropbox(DROPBOX_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

DATA_DIR = Path("data/quotes")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def list_and_download_files(folder_path=""):
    """
    Recursively Lists and downloads all files from the Dropbox folder.
    It handles nested folders by recursion.
    """
    try:
        res = dbx.files_list_folder(folder_path)
    except dropbox.exceptions.ApiError as err:
        print(f"Folder listing failed for {folder_path} -- maybe it is empty or path is wrong? {err}")
        return []

    downloaded_files = []

    def process_entries(entries):
        for entry in entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                print(f"Downloading {entry.path_display}...")
                local_path = DATA_DIR / Path(entry.path_display.lstrip('/'))
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    _, res = dbx.files_download(entry.path_lower)
                    with open(local_path, "wb") as f:
                        f.write(res.content)
                    print(f"Saved to {local_path}")
                    downloaded_files.append(local_path)
                except Exception as e:
                     print(f"Error downloading {entry.path_display}: {e}")

            elif isinstance(entry, dropbox.files.FolderMetadata):
                print(f"Scanning folder {entry.path_display}...")
                # Recursive call for subfolders
                downloaded_files.extend(list_and_download_files(entry.path_lower))
    
    process_entries(res.entries)

    # Handle pagination
    while res.has_more:
        res = dbx.files_list_folder_continue(res.cursor)
        process_entries(res.entries)
        
    return downloaded_files


def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def ingest_files(file_paths):
    # Ensure index exists
    if PINECONE_INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        print(f"Creating index {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index(PINECONE_INDEX_NAME)
    
    total_vectors = []
    
    for file_path in file_paths:
        try:
            # Simple text extraction based on extension
            if file_path.suffix.lower() == '.txt' or file_path.suffix.lower() == '.md' or file_path.suffix.lower() == '.csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif file_path.suffix.lower() == '.pdf':
                 try:
                     import pypdf
                     reader = pypdf.PdfReader(file_path)
                     content = ""
                     for page in reader.pages:
                         content += page.extract_text() + "\n"
                 except Exception as e:
                     print(f"Error reading PDF {file_path}: {e}")
                     continue
            else:
                print(f"Skipping unsupported file type: {file_path}")
                continue

            chunks = chunk_text(content)
            print(f"Processing {file_path.name}: {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                vector_id = str(uuid.uuid4())
                embedding = get_embedding(chunk)
                metadata = {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "text": chunk,
                    "type": "quotation_archive"
                }
                total_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Batch upsert
    batch_size = 100
    for i in range(0, len(total_vectors), batch_size):
        batch = total_vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1}/{(len(total_vectors)//batch_size)+1}")

if __name__ == "__main__":
    print("Starting Dropbox download...")
    # "" downloads from root if using an app folder specific token, otherwise we might need a path
    # If using full Dropbox access token, we might need a specific folder path. 
    # Attempting root first.
    files = list_and_download_files("") 
    
    if files:
        print(f"Downloaded {len(files)} files. Starting ingestion...")
        ingest_files(files)
        print("Done!")
    else:
        print("No files found or download failed.")
