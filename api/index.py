"""
Vercel Serverless Function entry point for Bank Statement Table Extraction API.
Exports the FastAPI application instance for @vercel/python runtime.
"""

import sys
import os

# Add root directory to sys.path so app packages are resolvable
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app
