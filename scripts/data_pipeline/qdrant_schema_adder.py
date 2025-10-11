from qdrant_client.http.models import PayloadSchemaType
from qdrant_client import QdrantClient
import os


fed_payload_schema = {
    "title": PayloadSchemaType.KEYWORD,
    "speaker": PayloadSchemaType.KEYWORD,
    "url": PayloadSchemaType.KEYWORD,
    "description": PayloadSchemaType.TEXT,
    "category": PayloadSchemaType.KEYWORD,
    "pub_date": PayloadSchemaType.KEYWORD,
    "content_length": PayloadSchemaType.INTEGER,
    "scraped_at": PayloadSchemaType.KEYWORD,
    "document": PayloadSchemaType.TEXT
}

def main(collection_name = "fed_speeches", schema = fed_payload_schema):
    """
    Adds a schema to a Qdrant collection by creating payload indexes.

    Args:
        collection_name (str): The name of the collection to update.
        schema (dict): The schema to add to the collection.

    Returns:
        None
    """
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables must be set")
    
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    try:
        # Create payload indexes one by one
        for field_name, field_type in schema.items():
            print(f"Creating index for field {field_name} with type {field_type}")
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=field_type
            )
        print(f"Schema added to collection '{collection_name}' successfully.")
    except Exception as e:
        print(f"An error occurred while adding schema to collection '{collection_name}': {e}")

if __name__ == "__main__":
    main()