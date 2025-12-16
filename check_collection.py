import chromadb
from chromadb.config import Settings
import os

# 配置连接到 Docker 里的 Chroma
CHROMA_HOST = "192.168.0.104"
CHROMA_PORT = "8012"

try:
    client = chromadb.HttpClient(
        host=CHROMA_HOST, 
        port=CHROMA_PORT,
        ssl=False
    )
    print(f"Connected to Chroma at {CHROMA_HOST}:{CHROMA_PORT}")
    
    colls = client.list_collections()
    print("Collections found:", [c.name for c in colls])
    
    if "techChat" in [c.name for c in colls]:
        coll = client.get_collection("techChat")
        print(f"\nCollection 'techChat' found.")
        print(f"Count: {coll.count()}")
        print(f"Metadata: {coll.metadata}")
        
        # 尝试查看一条数据，看它的向量维度
        peek = coll.peek(limit=1)
        embeddings = peek['embeddings']
        if embeddings is not None and len(embeddings) > 0:
            dim = len(embeddings[0])
            print(f"Embedding dimension: {dim}")
            if dim == 768:
                print("Dimension 768 suggests Gemini/OpenAI embeddings (likely).")
            elif dim == 384:
                print("Dimension 384 suggests Default all-MiniLM-L6-v2 embeddings.")
            else:
                print(f"Unknown dimension: {dim}")
    else:
        print("\nCollection 'techChat' NOT found.")

except Exception as e:
    print(f"Error: {e}")