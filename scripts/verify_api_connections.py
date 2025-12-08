import os
import requests
from dotenv import load_dotenv

# Load unified env
load_dotenv('.env.unified', override=True)

def test_openai_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("placeholder"):
        print("❌ OpenAI API Key is missing or placeholder.")
        return
    
    print(f"Testing OpenAI Key: {api_key[:8]}...")
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ OpenAI API Key is VALID (Models listed).")
        else:
            print(f"❌ OpenAI API Key check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")

def test_gemini_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("placeholder"):
        print("❌ Gemini API Key is missing or placeholder.")
        return

    print(f"Testing Gemini Key: {api_key[:8]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Gemini API Key is VALID (Models listed).")
        else:
            print(f"❌ Gemini API Key check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Gemini connection error: {e}")

def test_sheets_key():
    api_key = os.getenv("GOOGLE_SHEETS_API_KEY")
    if not api_key or api_key.startswith("placeholder"):
        print("❌ Google Sheets API Key is missing or placeholder.")
        return

    # To test a Sheets API key without a specific sheet, we can't do much easily unless we have a known public sheet or just check if the key is valid for *any* call.
    # We can try to access a public discovery document with the key, or just acknowledge it exists.
    # Verification of Sheets API key usually requires a call to a resource.
    # We will skip a network call for Sheets if we don't have a SHEET_ID, but warn about the ID.
    print(f"ℹ️  Google Sheets API Key present: {api_key[:8]}...")
    
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id or sheet_id.startswith("placeholder"):
        print("⚠️  GOOGLE_SHEET_ID is missing. Cannot verify API Key against a specific sheet.")
    else:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}?key={api_key}"
        try:
             response = requests.get(url, timeout=10)
             if response.status_code == 200:
                 print("✅ Google Sheets connection successful.")
             elif response.status_code == 403: # Permission denied often means key is valid but sheet is private or restricted
                 print(f"⚠️  Google Sheets Key valid but access denied (Check sheet permissions): {response.status_code}")
             else:
                 print(f"❌ Google Sheets Request failed: {response.status_code} - {response.text}")
        except Exception as e:
             print(f"❌ Google Sheets connection error: {e}")

if __name__ == "__main__":
    print("--- Verifying API Connections ---")
    test_openai_key()
    print("-" * 30)
    test_gemini_key()
    print("-" * 30)
    test_sheets_key()
    print("--- End Verification ---")
