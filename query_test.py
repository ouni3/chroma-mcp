import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os

# Configuration matching docker-compose.yaml
CHROMA_HOST = "192.168.0.104"
CHROMA_PORT = "8012"

# Embedding Configuration
os.environ["CHROMA_OPENAI_API_KEY"] = "sk-123456"
os.environ["CHROMA_OPENAI_API_BASE"] = "http://192.168.0.104:8000/v1"
os.environ["CHROMA_OPENAI_MODEL_NAME"] = "gemini-embedding-001"

def get_embedding_function():
    return OpenAIEmbeddingFunction(
        api_key=os.environ["CHROMA_OPENAI_API_KEY"],
        api_base=os.environ["CHROMA_OPENAI_API_BASE"],
        model_name=os.environ["CHROMA_OPENAI_MODEL_NAME"]
    )

try:
    print("Connecting to Chroma...")
    client = chromadb.HttpClient(
        host=CHROMA_HOST, 
        port=CHROMA_PORT,
        ssl=False
    )
    
    ef = get_embedding_function()
    
    print("Getting collection 'techChat'...")
    # Get collection without specifying EF (loads with default/384)
    collection = client.get_collection(name="techChat")
    
    # HACK: Manually swap the embedding function to the one we want (3072)
    # This bypasses the name check validation in get_collection
    collection._embedding_function = ef
    
    print("Querying for '链表'...")
    results = collection.query(
        query_texts=["链表"],
        n_results=3
    )
    
    print("\nResults:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"{i+1}. {doc[:100]}...") # Print first 100 chars
        
except Exception as e:
    print(f"Error: {e}")