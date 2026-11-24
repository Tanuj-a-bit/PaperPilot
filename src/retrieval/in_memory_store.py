"""In-memory Vector Store using Ephemeral ChromaDB Client."""

import chromadb
from src.llm.gemini_client import embed_texts, embed_query

class InMemoryVectorStore:
    def __init__(self, collection_name: str = "paperpilot_in_memory"):
        # chromadb.EphemeralClient keeps everything in RAM — zero local file writes
        self.client = chromadb.EphemeralClient()
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[dict]):
        """Adds text chunks with in-memory embeddings to the ephemeral collection."""
        if not chunks:
            return
        
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["text"] for c in batch]
            ids = [c["chunk_id"] for c in batch]
            metadatas = [{"paper_title": c["paper_title"], "page_num": c["page_num"]} for c in batch]
            
            # Generate embeddings via Gemini
            embeddings = embed_texts(texts)
            
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

    def search(self, query: str, top_k: int = 5, filter_paper: str = None) -> list[dict]:
        """Query top-k relevant chunks."""
        query_embedding = embed_query(query)
        where_clause = {"paper_title": filter_paper} if filter_paper else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        
        retrieved = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            for doc, meta, cid in zip(docs, metas, ids):
                retrieved.append({
                    "chunk_id": cid,
                    "text": doc,
                    "paper_title": meta.get("paper_title"),
                    "page_num": meta.get("page_num")
                })
        return retrieved

    def clear(self):
        """Reset and wipe in-memory collections."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
