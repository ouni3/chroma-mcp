import pytest
import os
import chromadb
from chromadb.utils import embedding_functions
from chroma_mcp.server import chroma_generate_keywords, get_chroma_client, _chroma_client
import sys
from unittest.mock import MagicMock, patch

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.mark.asyncio
async def test_chroma_generate_keywords():
    """Test keyword generation with mocked data to avoid dependency on real embeddings/OpenAI."""
    
    # Mock collection name
    collection_name = "test_keywords_collection"
    
    # Create dummy data
    documents = [
        "人工智能是未来的趋势",
        "机器学习是人工智能的一个子集",
        "深度学习使用神经网络",
        "自然语言处理帮助计算机理解人类语言",
        "Python是数据科学中最流行的语言",
        "Pandas用于数据分析",
        "NumPy用于数值计算",
        "Scikit-learn用于传统机器学习",
        "Chroma是一个向量数据库",
        "向量数据库用于存储和检索嵌入",
        "嵌入是文本的数值表示",
        "RAG增强了LLM的能力"
    ]
    
    # Mock embeddings (simple random vectors for clustering simulation)
    # 12 documents, 3 dimensions
    import numpy as np
    embeddings = np.random.rand(12, 3).tolist()
    
    # Mock Chroma Client and Collection
    with patch('chroma_mcp.server.get_chroma_client') as mock_get_client:
        mock_client = MagicMock()
        mock_collection = MagicMock()
        
        mock_get_client.return_value = mock_client
        mock_client.get_collection.return_value = mock_collection
        
        # Mock get() return value
        mock_collection.get.return_value = {
            'embeddings': embeddings,
            'documents': documents
        }
        
        # Run the function (Default Hybrid Mode)
        print(f"\nTesting keyword generation (Hybrid) for collection: {collection_name}")
        keywords = await chroma_generate_keywords(collection_name, n_clusters=3, top_k_per_cluster=2, use_hybrid_mode=True)
        
        print(f"Generated Keywords (Hybrid): {keywords}")
        
        # Assertions
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "__NO_DATA_FOUND__" not in keywords
        
        # Run the function (TextRank Only)
        print(f"\nTesting keyword generation (TextRank Only) for collection: {collection_name}")
        keywords_tr = await chroma_generate_keywords(collection_name, n_clusters=3, top_k_per_cluster=2, use_hybrid_mode=False)
        print(f"Generated Keywords (TextRank): {keywords_tr}")
        
        # Hybrid mode should generally return more or equal keywords than single mode
        # (Though not strictly guaranteed if sets overlap perfectly, but highly likely with different algos)
        assert len(keywords) >= len(keywords_tr)
        
@pytest.mark.asyncio
async def test_chroma_generate_keywords_empty():
    """Test handling of empty collection."""
    collection_name = "empty_collection"
    
    with patch('chroma_mcp.server.get_chroma_client') as mock_get_client:
        mock_client = MagicMock()
        mock_collection = MagicMock()
        
        mock_get_client.return_value = mock_client
        mock_client.get_collection.return_value = mock_collection
        
        # Mock empty result
        mock_collection.get.return_value = {
            'embeddings': None,
            'documents': None
        }
        
        keywords = await chroma_generate_keywords(collection_name)
        assert keywords == ["__NO_DATA_FOUND__"]

if __name__ == "__main__":
    # Manually run the async test if executed directly
    import asyncio
    try:
        asyncio.run(test_chroma_generate_keywords())
        print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()