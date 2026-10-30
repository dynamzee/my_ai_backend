import pathlib, requests
from config_settings import settings

API = "http://127.0.0.1:8000/documents/ingest"
HEADERS = {"X-API-Key": settings.api_key}
FOLDER = pathlib.Path(r"C:\Users\HP\OneDrive\Documents\MEDIUM_ARTICLES")

for path in sorted(FOLDER.glob("*.txt")):
    with open(path, "rb") as file:
        response = requests.post(API, headers=HEADERS, timeout=120,
                                 files={"file": (path.name, file, "text/plain")})
    if response.status_code == 200:
        print(f"INGESTED {path.name}: {response.json()['chunks_created']} chunks")
    else:
        print(f"FAILED {path.name}: {response.status_code} {response.text[:200]}")

