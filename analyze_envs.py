import os
import re


def get_keys(filepath):
    keys = set()
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    keys.add(key)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return keys


files = [
    ".env",
    ".env.unified",
    ".env.backup.20251204_232627",
    ".env.local.bak2",
    ".env.local.bak3",
    ".env.local.bak4",
]

base_keys = get_keys(".env")
print(f"Current .env has {len(base_keys)} keys")

for fname in files:
    if fname == ".env":
        continue
    if os.path.exists(fname):
        f_keys = get_keys(fname)
        missing = base_keys - f_keys
        extra = f_keys - base_keys
        print(f"\nFile: {fname}")
        print(f"  Keys matching .env: {len(base_keys & f_keys)}")
        print(f"  Keys missing from .env: {len(missing)}")
        print(f"  Extra keys not in .env: {len(extra)}")
        if extra:
            print(f"  Extra keys: {list(extra)}")
