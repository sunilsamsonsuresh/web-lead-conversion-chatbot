import os
import json
import sys
from dotenv import load_dotenv
import faiss

# Ensure parent directory is in sys.path for imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.indices.loading import load_index_from_storage
from utils.llm_model import embed_model

load_dotenv()

def prepare_documents(data):
    """
    Converts a list of dicts into llama_index Document objects.
    """
    documents = []
    for item in data:
        text = f"{item.get('title', '')}\n\n{item.get('passage', '')}"
        metadata = {
            "id": item.get("id"),
            "source": item.get("source"),
            "date": item.get("date")
        }
        documents.append(Document(text=text, metadata=metadata))
    return documents


def create_and_save_index(documents, index_dir="spanish-citizenship-service-faiss-index"):

    os.makedirs(index_dir, exist_ok=True)

    # ✅ Create FAISS index manually
    faiss_index = faiss.IndexFlatL2(1536)
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    # ✅ Attach FAISS to storage context
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    # ✅ Build index with FAISS-based storage
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    # ✅ Persist FAISS + metadata
    index.storage_context.persist(index_dir)
    print(f"FAISS index saved to {index_dir}")
    return index


def load_index(index_dir="spanish-citizenship-service-faiss-index"):

    faiss_path = os.path.join(index_dir)
    if not os.path.exists(faiss_path):
        raise FileNotFoundError(f"FAISS index file not found at: {faiss_path}")

    vector_store = FaissVectorStore.from_persist_dir(index_dir)

    storage_context = StorageContext.from_defaults(
        persist_dir=index_dir,
        vector_store=vector_store
    )

    index = load_index_from_storage(storage_context=storage_context)
    print(f"Index loaded from '{faiss_path}'")
    return index


def query_index(index, query_str):
    """
    Queries the loaded index and returns the response.
    """
    # Use the default query engine
    query_engine = index.as_query_engine()
    response = query_engine.query(query_str)
    return response

if __name__ == "__main__":
    # json_path = "indexing_data/spanish-citizenship-service.json"
    # if not os.path.exists(json_path):
    #     raise FileNotFoundError(f"JSON file not found at {json_path}")

    # with open(json_path, "r", encoding="utf-8") as f:
    #     sample_data = json.load(f)

    # # Prepare documents
    # docs = prepare_documents(sample_data)

    # # Create index and save to disk
    # index = create_and_save_index(docs)

    # Load index back from disk
    loaded_index = load_index(index_dir="spanish-citizenship-service-faiss-index")

    # Query example
    query = "How much does the Spanish citizenship package cost?"
    answer = query_index(loaded_index, query)
    print("Query response:", answer)
