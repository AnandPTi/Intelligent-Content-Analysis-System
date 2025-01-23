# vector_store.py
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import os
from pinecone import ServerlessSpec, Pinecone

load_dotenv()

class VectorStore:
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        except Exception as e:
            raise RuntimeError(f"Error initializing Pinecone: {e}")
        
        # Index name configuration
        self.index_name = "content-embeddings"

        # # Create the index if it doesn't exist
        # try:
        #     if self.index_name not in self.pc.list_indexes():
        #         self.pc.create_index(
        #             name=self.index_name,
        #             dimension=768,
        #             metric="cosine",
        #             spec=ServerlessSpec(
        #                 cloud="aws",
        #                 region="us-east-1"
        #             )
        #         )
        # except Exception as e:
        #     raise RuntimeError(f"Error creating Pinecone index: {e}")
        
        try:
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            raise RuntimeError(f"Error connecting to Pinecone index: {e}")

    async def store_embeddings(self, id: str, embeddings: List[float], metadata: Dict):
        """
        Store embeddings in the Pinecone index.
        """
        try:
            self.index.upsert(
                vectors=[(id, embeddings, metadata)],
            )
        except Exception as e:
            raise Exception(f"Failed to store embeddings: {str(e)}")
    async def search(self, query_embeddings: List[float], top_k: int = 5, filter: Dict = None):
        """
        Search for similar vectors in Pinecone
        """
        try:
            return self.index.query(
                vector=query_embeddings,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
        except Exception as e:
            raise Exception(f"Failed to search embeddings: {str(e)}")
        
    async def delete_vectors(self, ids: List[str]):
        """
        Delete vectors by their IDs
        """
        try:
            self.index.delete(ids=ids)
        except Exception as e:
            raise Exception(f"Failed to delete vectors: {str(e)}")

    async def fetch_vectors(self, ids: List[str]):
        """
        Fetch specific vectors by their IDs
        """
        try:
            return self.index.fetch(ids=ids)
        except Exception as e:
            raise Exception(f"Failed to fetch vectors: {str(e)}")
        
    async def get_metadata(self, id: str) -> Optional[Dict]:
        """
        Get metadata for a specific vector using fetch
        """
        try:
            result = self.index.fetch(ids=[id])
            
            if result and result.get('vectors') and id in result['vectors']:
                vector_data = result['vectors'][id]
                #return 
                return vector_data.get('metadata', {})

            else:
                return None
        except Exception as e:
            raise Exception(f"Failed to get metadata: {str(e)}")
