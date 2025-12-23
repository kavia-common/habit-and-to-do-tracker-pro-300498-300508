"""
Utility script to generate the OpenAPI schema file for this FastAPI app.

Usage:
  python -m src.api.generate_openapi

This will write interfaces/openapi.json with the current schema
as defined by src.api.main:app.
"""
import json
import os

from src.api.main import app

# Get the OpenAPI schema
openapi_schema = app.openapi()

# Write to file
output_dir = "interfaces"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "openapi.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
