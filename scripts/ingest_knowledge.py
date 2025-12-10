import os
import json
import time
from typing import List, Dict, Any
from pathlib import Path
import openai
import re
from pinecone import Pinecone, ServerlessSpec

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot-context")
DATA_FILE = Path(__file__).parent.parent / "conocimiento_consolidado.json"

def load_data(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_product_chunks(products: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = []
    for product_id, data in products.items():
        # Create a text representation for embedding
        nombre = data.get("nombre", "")
        base = data.get("caracteristicas_base", {})
        desc = base.get("descripcion", "")
        precio_info = data.get("precios_competitivos", {})
        
        # Construct rich context text
        text = f"Producto: {nombre}\n"
        text += f"Descripción: {desc}\n"
        
        if precio_info:
            prices_str = ", ".join([f"{k}: ${v}" for k, v in precio_info.items()])
            text += f"Precios: {prices_str}\n"

        # Metadata for filtering/retrieval
        metadata = {
            "type": "product",
            "product_id": product_id,
            "name": nombre,
            "text": text # Store text in metadata for easy retrieval
        }
        
        chunks.append({
            "id": f"prod_{re.sub(r'[^a-zA-Z0-9_-]', '_', product_id)}",
            "text": text,
            "metadata": metadata
        })
    return chunks

def get_embedding(text: str, client: openai.OpenAI) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def main():
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found.")
        return
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found.")
        return

    print(f"📥 Loading data from {DATA_FILE}...")
    try:
        data = load_data(DATA_FILE)
    except FileNotFoundError:
        print(f"❌ Error: Data file not found at {DATA_FILE}")
        return

    products = data.get("conocimiento_productos", {})
    print(f"📦 Found {len(products)} products.")

    chunks = create_product_chunks(products)
    print(f"🧩 Generated {len(chunks)} chunks.")

    # Initialize Clients
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create Index if not exists
    existing_indexes = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"🆕 Creating index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536, # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    
    index = pc.Index(PINECONE_INDEX_NAME)

    print("🚀 Starting ingestion...")
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        vectors = []
        
        for item in batch:
            try:
                embedding = get_embedding(item["text"], openai_client)
                vectors.append({
                    "id": item["id"],
                    "values": embedding,
                    "metadata": item["metadata"]
                })
            except Exception as e:
                print(f"⚠️ Error embedding item {item['id']}: {e}")
        
        if vectors:
            index.upsert(vectors=vectors)
            print(f"✅ Upserted batch {i//batch_size + 1}")

    print("🎉 Ingestion complete!")

if __name__ == "__main__":
    main()
