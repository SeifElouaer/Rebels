"""
config.py
---------
Configuration module for Qdrant vector store and Gemini LLM.

Centralizes all configuration parameters for easy management and testing.
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance

# Load environment variables from .env file
load_dotenv()

# Find project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Qdrant configuration: Use local storage by default for portability
# This allows the project to run without Docker!
QDRANT_STORAGE_PATH = os.path.join(BASE_DIR, "db", "qdrant_storage")

# Initialize Qdrant client
# If you want to use Docker, change this to: QdrantClient(host="localhost", port=6333)
QDRANT_CLIENT = QdrantClient(path=QDRANT_STORAGE_PATH)

# Collection configuration
COLLECTION_NAME = "loan_applications"
VECTOR_SIZE = 50
DISTANCE_METRIC = Distance.COSINE

# Optional: Batch processing settings
DEFAULT_BATCH_SIZE = 100
DEFAULT_TOP_K = 5

# LLM Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"