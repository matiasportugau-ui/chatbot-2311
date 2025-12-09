#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMC Chat API Proxy
Redirects to sistema_completo_integrado.py to support existing deployment config
"""

import os
import sys

# Ensure current directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the new application
try:
    from sistema_completo_integrado import app
except ImportError as e:
    print(f"Error importing sistema_completo_integrado: {e}")
    # Fallback for debugging
    from fastapi import FastAPI
    app = FastAPI(title="Error Loading App")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
