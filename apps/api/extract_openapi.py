import json
from app.main import app

def generate_openapi_json():
    # Force generating the schema
    openapi_schema = app.openapi()
    
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_openapi_json()
    print("Successfully generated openapi.json")
