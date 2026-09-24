from typing import Any, Dict, List, Optional

class HybridRAGEngine:
    def __init__(self):
        self.documents = []

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        self.documents.extend(documents)

    def hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        results = []

        for document in self.documents:
            content = document.get("text", "")
            metadata = document.get("metadata", {})

            if filters and any(
                metadata.get(key) != value
                for key, value in filters.items()
                if value is not None
            ):
                continue

            score = sum(
                1 for word in query_words
                if word in content.lower()
            )

            if score:
                results.append({
                    "text": content,
                    "score": float(score),
                    "metadata": metadata
                })

        return sorted(
            results,
            key=lambda result: result["score"],
            reverse=True
        )[:top_k]


# Upload, search, and chat must query the same in-process index.
rag_engine = HybridRAGEngine()