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
        self.embedding_fn = embedding_functions.HuggingFaceEmbeddingFunction(
            api_key=hf_token,
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Inicializamos el cliente
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
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

    async def search(self, pattern: str):
        # Implementa aquí tu lógica de búsqueda usando self.collection.query
        pass

# Instancia global perezosa
_semantic_instance = None

def get_semantic_memory():
    global _semantic_instance
    if _semantic_instance is None:
        _semantic_instance = SemanticMemory()
    return _semantic_instance

# Para mantener compatibilidad con tu main.py:
semantic_memory = get_semantic_memory()
