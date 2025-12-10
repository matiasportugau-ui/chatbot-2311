
import os
import json
import csv
import uuid
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
import openai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    print(f"Using OpenAI API Key ending in: ...{OPENAI_API_KEY[-4:]}")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "chatbot-context")

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

DATA_DIR = Path("data")
SHOPIFY_FILE = DATA_DIR / "shopify_products.json"
PRICES_FILE = DATA_DIR / "prices.csv"

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def clean_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def load_prices_from_csv():
    prices_map = {}
    if not PRICES_FILE.exists():
        print(f"Warning: {PRICES_FILE} not found. Skipping cost/updated price ingestion.")
        return prices_map

    print(f"Loading prices from {PRICES_FILE}...")
    try:
        with open(PRICES_FILE, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            # Normalize headers to lowercase to be safer
            headers = [h.lower() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Identify columns
            sku_col = next((h for h in reader.fieldnames if 'sku' in h.lower() or 'codigo' in h.lower()), None)
            cost_col = next((h for h in reader.fieldnames if 'cost' in h.lower() or 'costo' in h.lower()), None)
            price_col = next((h for h in reader.fieldnames if 'price' in h.lower() or 'precio' in h.lower()), None)
            
            if not sku_col:
                print("Could not identify SKU column in CSV. Available columns:", reader.fieldnames)
                return prices_map

            for row in reader:
                sku = row[sku_col].strip()
                if not sku:
                    continue
                
                data = {}
                if cost_col and row[cost_col]:
                    data['cost'] = row[cost_col]
                if price_col and row[price_col]:
                    data['price'] = row[price_col]
                
                prices_map[sku] = data
                
    except Exception as e:
        print(f"Error reading CSV: {e}")
        
    return prices_map

def ingest_products():
    # Ensure index exists
    existing_indexes = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"Creating index {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index(PINECONE_INDEX_NAME)
    
    if not SHOPIFY_FILE.exists():
        print(f"Error: {SHOPIFY_FILE} not found.")
        return

    print(f"Loading products from {SHOPIFY_FILE}...")
    with open(SHOPIFY_FILE, 'r', encoding='utf-8') as f:
        shopify_data = json.load(f)
    
    products = shopify_data.get('products', [])
    print(f"Found {len(products)} products in Shopify data.")

    prices_map = load_prices_from_csv()
    
    vectors_to_upsert = []
    
    for product in products:
        title = product.get('title', '')
        description_html = product.get('body_html', '')
        description = clean_html(description_html)
        vendor = product.get('vendor', '')
        product_type = product.get('product_type', '')
        
        for variant in product.get('variants', []):
            sku = variant.get('sku')
            if sku is None:
                sku = ""
            
            variant_title = variant.get('title', '')
            if variant_title == 'Default Title':
                variant_title = ''
            
            # Determine price and cost
            price = variant.get('price')
            if price is None:
                price = "0"
            
            cost = "N/A"
            
            # Override/Augment with CSV data if available
            if sku and sku in prices_map:
                csv_data = prices_map[sku]
                if 'price' in csv_data:
                    price = csv_data['price']
                if 'cost' in csv_data:
                    cost = csv_data['cost']
            
            full_title = f"{title} {variant_title}".strip()
            
            # Construct text text for embedding
            text_content = f"""
Product: {full_title}
SKU: {sku}
Price: {price}
Cost: {cost}
Vendor: {vendor}
Type: {product_type}
Description: {description}
            """.strip()
            
            vector_id = f"product_{variant['id']}" if variant.get('id') else str(uuid.uuid4())
            embedding = get_embedding(text_content)
            
            metadata = {
                "source": "shopify_product_ingestion",
                "product_id": str(product.get('id') or ""),
                "variant_id": str(variant.get('id') or ""),
                "sku": sku,
                "title": full_title,
                "price": str(price),
                "cost": str(cost),
                "type": "product_catalog",
                "text": text_content
            }
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })

    if not vectors_to_upsert:
        print("No vectors generated.")
        return

    print(f"Total product variants to upsert: {len(vectors_to_upsert)}")
    
    # Batch upsert
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i+batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert)//batch_size)+1}")
        except Exception as e:
            print(f"Error upserting batch: {e}")

if __name__ == "__main__":
    ingest_products()
