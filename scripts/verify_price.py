
import os
from pinecone import Pinecone
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
index = pc.Index(PINECONE_INDEX_NAME)

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def query_product(query_text):
    print(f"Querying: '{query_text}'")
    embedding = get_embedding(query_text)
    
    results = index.query(
        vector=embedding,
        top_k=3,
        include_metadata=True,
        filter={"type": "product_catalog"}
    )
    
    print("\n--- Results ---")
    for match in results['matches']:
        print(f"Score: {match['score']:.4f}")
        metadata = match['metadata']
        print(f"Product: {metadata.get('title')}")
        print(f"Price: {metadata.get('price')}")
        print(f"Text Snippet: {metadata.get('text')[:100]}...")
        print("-" * 20)

if __name__ == "__main__":
    query_product("precio de Embudo Conector de Bajada PVC para Canaleta (100mm)")
