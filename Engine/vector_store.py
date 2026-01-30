"""
vector_store.py
---------------
Vector database operations module for Qdrant.

This module handles all interactions with the Qdrant vector database including:
- Collection management
- Vector upsertion
- Similarity search operations

Note: This module does NOT handle:
- Embedding generation (handled by embedding modules)
- Data validation (handled by validation modules)
- Business logic (handled by application modules)
"""

from typing import List, Dict, Optional, Any
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from qdrant_client.http import models

# Import Qdrant configuration from config module
try:
    from config import (
        QDRANT_CLIENT,
        COLLECTION_NAME,
        VECTOR_SIZE,
        DISTANCE_METRIC
    )
except ImportError:
    # Fallback defaults if config.py doesn't exist
    # In production, you should always use config.py
    import os
    from qdrant_client import QdrantClient
    
    QDRANT_CLIENT = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )
    COLLECTION_NAME = "loan_applications"
    VECTOR_SIZE = 50
    DISTANCE_METRIC = Distance.COSINE

# Configure logging
logger = logging.getLogger(__name__)


def create_collection_if_not_exists() -> bool:
    """
    Create the Qdrant collection if it doesn't already exist.
    
    This function checks if the collection exists and creates it with the
    appropriate vector configuration if needed. It's idempotent and safe
    to call multiple times.
    
    Returns:
        bool: True if collection was created, False if it already existed
        
    Raises:
        Exception: If there's an error connecting to Qdrant or creating the collection
        
    Example:
        >>> create_collection_if_not_exists()
        True  # Collection was created
        
        >>> create_collection_if_not_exists()
        False  # Collection already exists
    """
    try:
        # Check if collection exists
        collections = QDRANT_CLIENT.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if COLLECTION_NAME in collection_names:
            logger.info(f"Collection '{COLLECTION_NAME}' already exists")
            return False
        
        # Create collection with vector configuration
        QDRANT_CLIENT.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_METRIC
            )
        )
        
        logger.info(
            f"Created collection '{COLLECTION_NAME}' "
            f"(size={VECTOR_SIZE}, distance={DISTANCE_METRIC})"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        raise Exception(f"Failed to create collection '{COLLECTION_NAME}': {str(e)}")


def upsert_vector(point_id: int, vector: List[float], payload: Dict[str, Any]) -> bool:
    """
    Insert or update a single vector in the collection.
    
    This function upserts (insert or update) a point with the given ID, vector,
    and payload into the Qdrant collection. If a point with the same ID exists,
    it will be updated.
    
    Args:
        point_id: Unique identifier for the point (must be non-negative integer)
        vector: The embedding vector as a list of floats
        payload: Metadata dictionary to store with the vector
        
    Returns:
        bool: True if upsert was successful
        
    Raises:
        ValueError: If vector dimensions don't match VECTOR_SIZE or point_id is invalid
        Exception: If there's an error upserting to Qdrant
        
    Example:
        >>> vector = [0.1, 0.2, 0.3, ...]  # 50 dimensions
        >>> payload = {
        ...     "application_id": "APP_12345",
        ...     "requested_amount": 10000,
        ...     "outcome": "success"
        ... }
        >>> upsert_vector(point_id=1, vector=vector, payload=payload)
        True
    """
    # Validate inputs
    if not isinstance(point_id, int) or point_id < 0:
        raise ValueError(f"point_id must be a non-negative integer, got: {point_id}")
    
    if not isinstance(vector, list) or len(vector) != VECTOR_SIZE:
        raise ValueError(
            f"Vector must be a list of {VECTOR_SIZE} floats, "
            f"got {len(vector) if isinstance(vector, list) else type(vector)}"
        )
    
    if not isinstance(payload, dict):
        raise ValueError(f"Payload must be a dictionary, got: {type(payload)}")
    
    try:
        # Create point structure
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )
        
        # Upsert to Qdrant
        QDRANT_CLIENT.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        logger.debug(f"Upserted point {point_id} to collection '{COLLECTION_NAME}'")
        return True
        
    except Exception as e:
        logger.error(f"Error upserting point {point_id}: {str(e)}")
        raise Exception(f"Failed to upsert point {point_id}: {str(e)}")


def search_similar(
    vector: List[float],
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for the most similar vectors in the collection.
    
    Performs a similarity search using cosine distance and returns the top_k
    most similar results. Optionally applies filters to narrow the search space.
    
    Args:
        vector: The query vector to search for similar items
        top_k: Number of most similar results to return (default: 5)
        filters: Optional dictionary of filters to apply to the search.
                Format: {"field_name": "value"} or {"field_name": {"$gte": value}}
                
    Returns:
        List of payload dictionaries from matching points, ordered by similarity.
        Each dictionary contains the metadata that was stored with the vector.
        Returns empty list if no results found.
        
    Raises:
        ValueError: If vector dimensions don't match VECTOR_SIZE or top_k is invalid
        Exception: If there's an error searching Qdrant
        
    Example:
        >>> query_vector = [0.1, 0.2, 0.3, ...]  # 50 dimensions
        >>> results = search_similar(vector=query_vector, top_k=5)
        >>> for result in results:
        ...     print(f"App ID: {result['application_id']}, Amount: {result['requested_amount']}")
        
        >>> # Search with filters
        >>> results = search_similar(
        ...     vector=query_vector,
        ...     top_k=10,
        ...     filters={"outcome": "success"}
        ... )
    """
    # Validate inputs
    if not isinstance(vector, list) or len(vector) != VECTOR_SIZE:
        raise ValueError(
            f"Vector must be a list of {VECTOR_SIZE} floats, "
            f"got {len(vector) if isinstance(vector, list) else type(vector)}"
        )
    
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError(f"top_k must be a positive integer, got: {top_k}")
    
    try:
        # Build Qdrant filter if provided
        query_filter = None
        if filters:
            # Convert simple dict filters to Qdrant Filter format
            must_conditions = []
            
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Handle range queries like {"$gte": 1000}
                    for operator, operand in value.items():
                        if operator == "$gte":
                            must_conditions.append(
                                models.FieldCondition(
                                    key=field,
                                    range=models.Range(gte=operand)
                                )
                            )
                        elif operator == "$lte":
                            must_conditions.append(
                                models.FieldCondition(
                                    key=field,
                                    range=models.Range(lte=operand)
                                )
                            )
                        elif operator == "$gt":
                            must_conditions.append(
                                models.FieldCondition(
                                    key=field,
                                    range=models.Range(gt=operand)
                                )
                            )
                        elif operator == "$lt":
                            must_conditions.append(
                                models.FieldCondition(
                                    key=field,
                                    range=models.Range(lt=operand)
                                )
                            )
                else:
                    # Handle exact match
                    must_conditions.append(
                        models.FieldCondition(
                            key=field,
                            match=models.MatchValue(value=value)
                        )
                    )
            
            if must_conditions:
                query_filter = models.Filter(must=must_conditions)
        
        # Perform search using the modern query_points API
        search_results = QDRANT_CLIENT.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k,
            query_filter=query_filter
        )
        
        # Extract payloads and scores from results
        results = [
            {"payload": hit.payload, "score": hit.score}
            for hit in search_results.points
        ]
        
        logger.debug(
            f"Search returned {len(results)} results out of top_{top_k} requested"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching similar vectors: {str(e)}")
        raise Exception(f"Failed to search similar vectors: {str(e)}")


def batch_upsert_vectors(
    points_data: List[tuple[int, List[float], Dict[str, Any]]],
    batch_size: int = 100
) -> int:
    """
    Upsert multiple vectors in batches for better performance.
    
    This is a utility function for bulk operations. It processes the data
    in batches to avoid overwhelming the server and provides better performance
    than individual upserts.
    
    Args:
        points_data: List of tuples, each containing (point_id, vector, payload)
        batch_size: Number of points to upsert per batch (default: 100)
        
    Returns:
        int: Total number of points successfully upserted
        
    Raises:
        ValueError: If any point data is invalid
        Exception: If there's an error during batch upsert
        
    Example:
        >>> data = [
        ...     (1, [0.1, 0.2, ...], {"app_id": "A1"}),
        ...     (2, [0.3, 0.4, ...], {"app_id": "A2"}),
        ...     # ... more points
        ... ]
        >>> count = batch_upsert_vectors(data, batch_size=100)
        >>> print(f"Upserted {count} points")
    """
    if not points_data:
        logger.warning("No points provided for batch upsert")
        return 0
    
    try:
        total_uploaded = 0
        
        for i in range(0, len(points_data), batch_size):
            batch = points_data[i:i + batch_size]
            
            # Validate and create PointStruct objects
            points = []
            for point_id, vector, payload in batch:
                if not isinstance(point_id, int) or point_id < 0:
                    raise ValueError(f"Invalid point_id: {point_id}")
                
                if len(vector) != VECTOR_SIZE:
                    raise ValueError(
                        f"Point {point_id}: vector size {len(vector)} "
                        f"doesn't match expected {VECTOR_SIZE}"
                    )
                
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )
            
            # Upsert batch
            QDRANT_CLIENT.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            
            total_uploaded += len(points)
            
            if total_uploaded % 1000 == 0 or total_uploaded == len(points_data):
                logger.info(
                    f"Batch upsert progress: {total_uploaded}/{len(points_data)} points"
                )
        
        logger.info(f"Successfully upserted {total_uploaded} points in total")
        return total_uploaded
        
    except Exception as e:
        logger.error(f"Error during batch upsert: {str(e)}")
        raise Exception(f"Failed to batch upsert vectors: {str(e)}")


def delete_collection() -> bool:
    """
    Delete the entire collection from Qdrant.
    
    WARNING: This is a destructive operation and cannot be undone.
    Use with caution, typically only during testing or reinitialization.
    
    Returns:
        bool: True if collection was deleted, False if it didn't exist
        
    Raises:
        Exception: If there's an error deleting the collection
        
    Example:
        >>> delete_collection()
        True  # Collection was deleted
    """
    try:
        collections = QDRANT_CLIENT.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if COLLECTION_NAME not in collection_names:
            logger.info(f"Collection '{COLLECTION_NAME}' does not exist")
            return False
        
        QDRANT_CLIENT.delete_collection(collection_name=COLLECTION_NAME)
        logger.info(f"Deleted collection '{COLLECTION_NAME}'")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise Exception(f"Failed to delete collection '{COLLECTION_NAME}': {str(e)}")


def get_collection_info() -> Dict[str, Any]:
    """
    Get information about the current collection.
    
    Returns:
        Dictionary containing collection metadata including:
        - exists: Whether the collection exists
        - vectors_count: Number of vectors in the collection
        - config: Collection configuration details
        
    Raises:
        Exception: If there's an error retrieving collection info
        
    Example:
        >>> info = get_collection_info()
        >>> print(f"Collection has {info['vectors_count']} vectors")
    """
    try:
        collections = QDRANT_CLIENT.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if COLLECTION_NAME not in collection_names:
            return {
                "exists": False,
                "vectors_count": 0,
                "config": None
            }
        
        collection_info = QDRANT_CLIENT.get_collection(collection_name=COLLECTION_NAME)
        
        
        return {
            "exists": True,
            "vectors_count": collection_info.points_count,  # Changed from vectors_count
            "config": {
                "vector_size": collection_info.config.params.vectors.size,
                "distance": str(collection_info.config.params.vectors.distance),
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise Exception(f"Failed to get collection info: {str(e)}")