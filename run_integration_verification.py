import subprocess
import sys
import os

def run_step(command, step_name):
    print(f"\n=== {step_name} ===")
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Execution Error: {e}")
        return 1

def main():
    python_exe = sys.executable
    
    # Check Environment
    mongodb_uri = os.getenv("MONGODB_URI", "")
    is_atlas = "mongodb+srv" in mongodb_uri
    
    print(f"ℹ️ Environment: {'Atlas Cloud' if is_atlas else 'Local MongoDB'}")
    
    # 1. Setup Atlas (Skip if Local)
    if is_atlas:
        c1 = run_step(f"{python_exe} scripts/setup_atlas_vector_search.py", "1. Setup Atlas Vector Search")
    else:
        print("\n=== 1. Setup Atlas Vector Search ===")
        print("⏭️ SKIPPED: Running on Local MongoDB (Vector Search not supported/needed).")
        c1 = 0

    # 2. Backfill
    # We use 'scripts/migrate_knowledge_to_mongo.py' based on file list availability, or fallback to backfill_embeddings.py
    # Let's check which one exists
    script_2 = "scripts/migrate_knowledge_to_mongo.py"
    if not os.path.exists(script_2):
        script_2 = "scripts/backfill_embeddings.py"
        
    c2 = run_step(f"{python_exe} {script_2}", "2. Data Migration / Backfill")
    
    # 3. Test RAG
    c3 = run_step(f"{python_exe} tests/test_rag_retrieval.py", "3. Verify RAG Retrieval")
    
    if c1 == 0 and c2 == 0 and c3 == 0:
        print("\n✅ SUCCESS: All applicable integration steps passed.")
        return 0
    else:
        print("\n❌ FAILURE: One or more steps failed.")
        return 1

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env.unified", override=True)
    
    # Fix placeholder Project ID issue
    if os.getenv("OPENAI_PROJECT_ID") == "placeholder_openai_project_id":
        os.environ.pop("OPENAI_PROJECT_ID", None)
        
    sys.exit(main())
