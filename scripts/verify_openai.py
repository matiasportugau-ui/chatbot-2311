
import os
import openai
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
print(f"Loaded key: {api_key[:10]}...{api_key[-4:]}")

client = openai.OpenAI(api_key=api_key)

try:
    resp = client.embeddings.create(
        input="test",
        model="text-embedding-3-small"
    )
    print("Success! Embedding generated.")
except Exception as e:
    print(f"Error: {e}")
