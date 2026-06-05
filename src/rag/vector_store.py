import os
import chromadb
from chromadb.config import Settings
import pandas as pd

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="dataset_columns",
            metadata={"hnsw:space": "cosine"}
        )
        
    def embed_dataset_columns(self, df: pd.DataFrame, dataset_name: str = "current_dataset"):
        """
        Embed the column names and sample data mapping them to their purpose
        so the LLM can know which columns exist and what they contain.
        """
        # Clear previous for simplicity in this single-dataset flow
        try:
            old_docs = self.collection.get()
            if old_docs and len(old_docs['ids']) > 0:
                self.collection.delete(ids=old_docs['ids'])
        except Exception:
            pass

        documents = []
        metadatas = []
        ids = []
        
        for i, col in enumerate(df.columns):
            dtype = str(df[col].dtype)
            sample_vals = df[col].dropna().head(3).tolist()
            doc_text = f"Column Name: {col}. Data Type: {dtype}. Sample Values: {sample_vals}."
            
            documents.append(doc_text)
            metadatas.append({"column": col, "type": dtype})
            ids.append(f"col_{i}")
            
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Embedded {len(df.columns)} columns into ChromaDB.")

    def search_relevant_columns(self, query: str, n_results: int = 5):
        """
        Retrieve the most relevant columns for a user's natural language query.
        """
        if self.collection.count() == 0:
            return []
            
        n_results = min(n_results, self.collection.count())
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format the retrieved documents
        if results['documents'] and len(results['documents']) > 0:
            return results['documents'][0]
        return []
