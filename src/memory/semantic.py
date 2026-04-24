import chromadb
from langchain_openai import OpenAIEmbeddings
import os

class SemanticMemory:
    def __init__(self):
        # We will use Chroma HTTP Client connecting to docker
        chroma_url = os.getenv("CHROMA_URL", "http://localhost:8000")
        host = chroma_url.split("://")[1].split(":")[0]
        port = chroma_url.split("://")[1].split(":")[1]
        
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
        except Exception as e:
            # Fallback to ephemeral if docker not reachable (for robustness)
            print(f"Warning: Could not connect to ChromaDB at {chroma_url}. Using EphemeralClient.")
            self.client = chromadb.EphemeralClient()
            
        self.collection_name = "semantic_knowledge"
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(name=self.collection_name)
            
        self.embeddings = OpenAIEmbeddings()

    def save_knowledge(self, document_id: str, text: str, metadata: dict = None):
        """Save a factual piece of knowledge to semantic memory."""
        embedding = self.embeddings.embed_query(text)
        self.collection.upsert(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else [{}],
            ids=[document_id]
        )

    def search_knowledge(self, query: str, n_results: int = 2) -> str:
        """Search for relevant knowledge."""
        if self.collection.count() == 0:
            return ""
            
        query_embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        formatted = ""
        for doc in results['documents'][0]:
            formatted += f"- {doc}\n"
        return formatted

    def clear(self):
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
        except Exception:
            pass
