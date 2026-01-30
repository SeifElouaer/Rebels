from qdrant_client import QdrantClient
import os

# Find project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QDRANT_STORAGE_PATH = os.path.join(BASE_DIR, "..", "db", "qdrant_storage")

client = QdrantClient(path=QDRANT_STORAGE_PATH)
try:
    collection_info = client.get_collection(collection_name="loan_applications")
    print(f"Vectors found: {collection_info.points_count}")
except Exception as e:
    print(f"Error: {e}")
