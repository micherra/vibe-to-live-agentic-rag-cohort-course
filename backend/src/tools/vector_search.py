"""
Vector search tool using Qdrant with FastEmbed for document retrieval.

STUDENT TODO: Complete the implementation of this vector search tool.
Follow the hints and complete the sections marked with TODO.

Learning Objectives:
- Understand how to connect to Qdrant
- Learn about environment variable handling
- Implement semantic search with FastEmbed
- Format and return search results
"""

import os
from qdrant_client import QdrantClient, models

class VectorSearchTool:
    """
    Tool for performing semantic search using Qdrant vector database with FastEmbed.

    This tool:
    1. Accepts a user query
    2. Uses FastEmbed (via Qdrant) to automatically generate embeddings
    3. Searches Qdrant for similar documents
    4. Returns relevant chunks with metadata
    
    Note: This implementation uses FastEmbed through Qdrant's query_points method,
    which automatically handles embedding generation on both ingestion and query time.
    """

    def __init__(
        self, 
        qdrant_url: str = None, 
        qdrant_api_key: str = None,
        collection_name: str = "fed_speeches",
        model_name: str = "BAAI/bge-small-en"
    ):
        """
        Initialize Qdrant client with FastEmbed support.
        
        Args:
            qdrant_url: Qdrant server URL (defaults to QDRANT_URL env var)
            qdrant_api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
            collection_name: Name of the collection (defaults to 'fed_speeches')
            model_name: FastEmbed model name (defaults to 'BAAI/bge-small-en')
        """
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        self.qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")

        if not self.qdrant_url or not self.qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be provided")
                
        self.qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        
        self.collection_name = collection_name
        self.model_name = model_name

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        Search for relevant documents in Qdrant using FastEmbed.

        Args:
            query: User's search query
            limit: Maximum number of results to return

        Returns:
            List of dictionaries containing:
            - content: Document content
            - metadata: Document metadata (title, speaker, date, etc.)
            - score: Similarity score
        """
        document = models.Document(text=query, model=self.model_name)
        
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=document,
            limit=limit
        )
        
        # Format results into a list of dictionaries.
        # The client returns an object with a `.points` list in our tests.
        points = getattr(search_results, "points", None)
        if points is None:
            # Fallback: if the mock returns a list directly
            points = search_results
        
        if not points:
            return []
        
        formatted_results = []
        for result in points:
            payload = getattr(result, "payload", {}) or {}
            score = getattr(result, "score", 0.0)
            formatted_result = {
                "content": payload.get("document", ""),
                "metadata": {
                    "title": payload.get("title", ""),
                    "speaker": payload.get("speaker", ""),
                    "pub_date": payload.get("pub_date", ""),
                    "category": payload.get("category", ""),
                    "url": payload.get("url", ""),
                    "description": payload.get("description", ""),
                    "content_length": payload.get("content_length", 0),
                    "scraped_at": payload.get("scraped_at", ""),
                },
                "score": score,
            }
            formatted_results.append(formatted_result)
        
        return formatted_results

    def verify_collection(self) -> dict:
        """
        Verify that the collection exists and return its info.
        
        Returns:
            Dictionary with collection information
        """
        # TODO 7: Try to get collection info and handle errors
        # Hint: Use a try/except block
        # Hint: Call self.qdrant_client.get_collection(self.collection_name)
        # Hint: If successful, return a dict with exists=True and collection info
        # Hint: If an exception occurs, return a dict with exists=False and error message
        
        try:
            # Get collection information from Qdrant
            collection_info = self.qdrant_client.get_collection(self.collection_name)

            # Prefer nested config (Qdrant >=1.7), fallback to top-level attributes
            points_count = getattr(collection_info, "points_count", None)
            try:
                vector_cfg = collection_info.config.params.vectors
                vector_size = getattr(vector_cfg, "size", None)
                distance = getattr(vector_cfg, "distance", None)
            except Exception:
                vector_size = getattr(collection_info, "vector_size", None)
                distance = getattr(collection_info, "distance", None)

            return {
                "exists": True,
                "points_count": points_count,
                "vector_size": vector_size,
                "distance": distance,
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
            }


# Tool function for OpenAI Agents SDK
def search_knowledge_base(query: str, limit: int = 5) -> str:
    """
    Search the knowledge base for relevant information.

    This function is designed to be used as a tool with OpenAI Agents SDK.

    Args:
        query: User's search query
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted string with search results
    """
    # TODO 8: Implement the search_knowledge_base function
    # Hint: This function wraps VectorSearchTool for use with OpenAI Agents
    # Hint: Use a try/except block to handle errors gracefully
    
    try:
        # TODO: Create VectorSearchTool instance
        tool = VectorSearchTool()
        
        # TODO: Perform search
        results = tool.search(query, limit=limit)
        
        # TODO: Check if results are empty
        if not results:
            return f"No results found for query: '{query}'"
        
        # TODO: Format results as a readable string
        # Include: number of documents, and for each result:
        #   - Result number and score
        #   - Title, Speaker, Date, Category
        #   - Content snippet (first 300 characters)

        result_summary = f"Found {len(results)} relevant documents\n"
        for i, result in enumerate(results, start=1):
            title = result["metadata"].get("title", "N/A")
            speaker = result["metadata"].get("speaker", "N/A")
            pub_date = result["metadata"].get("pub_date", "N/A")
            category = result["metadata"].get("category", "N/A")
            content_snippet = result["content"][:300].replace("\n", " ")
            score = result["score"]

            document_summary = (
                f"\n\nResult {i} (Score: {score:.4f}):\n"
                f"Title: {title}\n"
                f"Speaker: {speaker}\n"
                f"Date: {pub_date}\n"
                f"Category: {category}\n"
                f"Content Snippet: {content_snippet}..."
            )
            result_summary += document_summary + "\n"

        return result_summary.strip()
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"