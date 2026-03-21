import os
import json
import datetime
from typing import List, Dict, Any, Optional
from utils.logger import Logger
from utils.config import config

class SemanticMemory:
    def __init__(self, persist_directory: str = "data/db/chroma"):
        # Importación local para evitar el trigger de ONNX al inicio
        import chromadb
        from chromadb.utils import embedding_functions
        
        self.persist_directory = os.path.abspath(persist_directory)
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory, exist_ok=True)

        # Usamos tu token de Hugging Face
        hf_token = os.getenv("HF_TOKEN")
        # Ensure we use the router API to avoid the deprecated endpoint error
        self.embedding_fn = embedding_functions.HuggingFaceEmbeddingFunction(
            api_key=hf_token,
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # Monkey patch the URL if the library hasn't updated it yet
        if hasattr(self.embedding_fn, "_api_url"):
             if "api-inference.huggingface.co" in self.embedding_fn._api_url:
                 self.embedding_fn._api_url = self.embedding_fn._api_url.replace(
                     "api-inference.huggingface.co", "router.huggingface.co"
                 )

        # Inicializamos el cliente con telemetría desactivada
        from chromadb.config import Settings
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # IMPORTANTE: Al obtener la colección, pasamos la función de HF 
        # para que NUNCA use la de ONNX por defecto
        self.collection = self.client.get_or_create_collection(
            name="vulnerabilities",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        Logger.info(f"Semantic Memory operativa en {self.persist_directory}")

    async def store(self, target: str, vulnerability: str, context: Dict[str, Any]):
        try:
            timestamp = datetime.datetime.now().isoformat()
            doc_id = f"{target}_{timestamp}".replace(" ", "_")
            self.collection.add(
                documents=[f"Vulnerability: {vulnerability}"],
                metadatas=[{"target": target, "context": json.dumps(context)}],
                ids=[doc_id]
            )
        except Exception as e:
            Logger.error(f"Error store: {e}")

    async def search(self, pattern: str, n_results: int = 5):
        try:
            results = self.collection.query(
                query_texts=[pattern],
                n_results=n_results
            )

            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "vulnerability": results['documents'][0][i],
                        "target": results['metadatas'][0][i].get("target"),
                        "context": json.loads(results['metadatas'][0][i].get("context", "{}")),
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            return formatted_results
        except Exception as e:
            Logger.error(f"Error search: {e}")
            return []

# Instancia global perezosa
_semantic_instance = None

def get_semantic_memory():
    global _semantic_instance
    if _semantic_instance is None:
        _semantic_instance = SemanticMemory()
    return _semantic_instance

# Para mantener compatibilidad con tu main.py:
semantic_memory = get_semantic_memory()
