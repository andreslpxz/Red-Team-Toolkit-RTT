import chromadb
from chromadb.config import Settings
from utils.logger import Logger
from utils.config import config
import os
import json
from typing import List, Dict, Any, Optional
import datetime

class SemanticMemory:
    """
    Semantic memory implementation using ChromaDB to store and retrieve
    vulnerability patterns and exploitation history.
    """
    def __init__(self, persist_directory: str = "data/db/chroma"):
        self.persist_directory = persist_directory
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)

        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="vulnerabilities",
            metadata={"hnsw:space": "cosine"}
        )
        Logger.info("Semantic Memory initialized with ChromaDB.")

    async def store(self, target: str, vulnerability: str, context: Dict[str, Any]):
        """
        Stores a vulnerability and its context in the semantic memory.
        """
        try:
            timestamp = datetime.datetime.now().isoformat()
            doc_id = f"{target}_{timestamp}_{vulnerability[:20]}".replace(" ", "_")

            # Metadata must be simple types for ChromaDB
            metadata = {
                "target": target,
                "vulnerability": vulnerability,
                "timestamp": timestamp,
                "context_json": json.dumps(context)
            }

            self.collection.add(
                documents=[f"Vulnerability: {vulnerability}. Context: {json.dumps(context)}"],
                metadatas=[metadata],
                ids=[doc_id]
            )
            Logger.success(f"Stored semantic memory for {vulnerability} at {target}")
        except Exception as e:
            Logger.error(f"Failed to store semantic memory: {e}")

    async def remember(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves similar vulnerabilities or patterns from memory.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            findings = []
            if results['metadatas']:
                for meta in results['metadatas'][0]:
                    findings.append({
                        "target": meta.get("target"),
                        "vulnerability": meta.get("vulnerability"),
                        "timestamp": meta.get("timestamp"),
                        "context": json.loads(meta.get("context_json", "{}"))
                    })
            return findings
        except Exception as e:
            Logger.error(f"Failed to retrieve from semantic memory: {e}")
            return []

    async def search(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Semantic search for a specific pattern.
        """
        return await self.remember(pattern)

    async def analyze_pattern(self, vulnerability_info: str) -> Optional[str]:
        """
        Analyzes a new vulnerability against past experiences to suggest tactics.
        """
        similar = await self.remember(vulnerability_info, n_results=3)
        if not similar:
            return "No previous patterns found for this vulnerability."

        analysis = f"Found {len(similar)} similar patterns in history:\n"
        for i, item in enumerate(similar):
            analysis += f"- Case {i+1}: {item['vulnerability']} at {item['target']}\n"
            analysis += f"  Context: {item['context'].get('notes', 'N/A')}\n"

        return analysis

# Global instance
semantic_memory = SemanticMemory()
