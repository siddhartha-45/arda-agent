"""
Vector Memory - FAISS-based semantic memory with embeddings
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from sentence_transformers import SentenceTransformer
import pickle


class VectorMemory:
    """FAISS-based semantic memory system"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """
        Initialize vector memory

        Args:
            model_name: Sentence transformer model name
            dimension: Embedding dimension (depends on model)
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.entries = {}
        self.entry_list = []
        self.metadata = {}
        self.persistence_path = "vector_memory.pkl"

    def add(
        self,
        entry_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add text entry with embedding to memory

        Args:
            entry_id: Unique entry identifier
            text: Text content to embed
            metadata: Optional metadata about the entry
        """
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True).astype('float32')
        embedding = embedding.reshape(1, -1)

        # Add to index
        self.index.add(embedding)

        # Store entry data
        self.entries[entry_id] = text
        self.entry_list.append(entry_id)
        self.metadata[entry_id] = metadata or {}

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar entries

        Args:
            query: Query text
            top_k: Number of top results to return

        Returns:
            List of matching entries with similarity scores
        """
        if len(self.entry_list) == 0:
            return []

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True).astype('float32')
        query_embedding = query_embedding.reshape(1, -1)

        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.entry_list)))

        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= 0 and idx < len(self.entry_list):
                entry_id = self.entry_list[idx]
                # Convert L2 distance to similarity score
                similarity = 1.0 / (1.0 + float(distance))

                results.append({
                    'entry_id': entry_id,
                    'text': self.entries.get(entry_id, ''),
                    'similarity': similarity,
                    'metadata': self.metadata.get(entry_id, {}),
                    'rank': i + 1
                })

        return results

    def batch_add(self, entries: List[Dict[str, Any]]) -> None:
        """
        Add multiple entries in batch

        Args:
            entries: List of dicts with 'entry_id', 'text', and optional 'metadata'
        """
        for entry in entries:
            self.add(
                entry.get('entry_id'),
                entry.get('text'),
                entry.get('metadata')
            )

    def build_index(self) -> None:
        """Build optimized index (can be called after batch adds)"""
        # FAISS updates incrementally, but can optimize after bulk adds
        if self.index.ntotal > 1000:
            # Index is getting large, could implement more complex indexing
            pass

    def get(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific entry by ID"""
        if entry_id not in self.entries:
            return None

        return {
            'entry_id': entry_id,
            'text': self.entries[entry_id],
            'metadata': self.metadata.get(entry_id, {})
        }

    def delete(self, entry_id: str) -> bool:
        """Delete entry (marks as deleted in metadata)"""
        if entry_id in self.entries:
            self.metadata[entry_id]['deleted'] = True
            return True
        return False

    def update(
        self,
        entry_id: str,
        new_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update entry (delete and re-add with new embedding)

        Args:
            entry_id: Entry identifier
            new_text: New text content
            metadata: Optional updated metadata
        """
        # For FAISS, we would need to rebuild index
        # For now, we update the stored text
        if entry_id in self.entries:
            self.entries[entry_id] = new_text
            if metadata:
                self.metadata[entry_id].update(metadata)

    def clear(self) -> None:
        """Clear all entries from memory"""
        self.index.reset()
        self.entries.clear()
        self.entry_list.clear()
        self.metadata.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'total_entries': len(self.entry_list),
            'index_size': self.index.ntotal,
            'model': self.model.get_sentence_embedding_dimension()
        }

    def save(self, filepath: str = None) -> None:
        """Save memory to disk"""
        filepath = filepath or self.persistence_path
        data = {
            'entries': self.entries,
            'entry_list': self.entry_list,
            'metadata': self.metadata
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        faiss.write_index(self.index, f"{filepath}.index")

    def load(self, filepath: str = None) -> None:
        """Load memory from disk"""
        filepath = filepath or self.persistence_path
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            self.entries = data['entries']
            self.entry_list = data['entry_list']
            self.metadata = data['metadata']

            if os.path.exists(f"{filepath}.index"):
                self.index = faiss.read_index(f"{filepath}.index")
