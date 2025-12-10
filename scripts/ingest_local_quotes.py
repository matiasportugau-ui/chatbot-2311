
import os
import uuid
import re
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot-context")

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

DATA_DIR = Path("data/quotes")

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

def ingest_local_files():
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
    files = list(DATA_DIR.rglob("*"))
    print(f"Scanning {len(files)} files in {DATA_DIR}...")

    for file_path in files:
        if not file_path.is_file():
            continue
            
        try:
            content = ""
            if file_path.suffix.lower() in ['.txt', '.md', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif file_path.suffix.lower() == '.pdf':
                 try:
                     import pypdf
                     reader = pypdf.PdfReader(file_path)
                     for page in reader.pages:
                         content += page.extract_text() + "\n"
                 except Exception as e:
                     print(f"Error reading PDF {file_path}: {e}")
                     continue
            else:
                # print(f"Skipping unsupported file type: {file_path}")
                continue

            if not content.strip():
                continue

            chunks = chunk_text(content)
            # print(f"Processing {file_path.name}: {len(chunks)} chunks")
            
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

    if not total_vectors:
        print("No valid content found to ingest.")
        return

    print(f"Total vectors to upsert: {len(total_vectors)}")
    
    # Batch upsert
    batch_size = 100
    for i in range(0, len(total_vectors), batch_size):
        batch = total_vectors[i:i+batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"Upserted batch {i//batch_size + 1}/{(len(total_vectors)//batch_size)+1}")
        except Exception as e:
            print(f"Error upserting batch: {e}")

if __name__ == "__main__":
    if not DATA_DIR.exists():
        print(f"Directory {DATA_DIR} does not exist.")
    else:
        ingest_local_files()
        print("Done!")
