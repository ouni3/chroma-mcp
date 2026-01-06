# 任务：实现基于向量聚类的关键词生成功能 (generate_keywords)

## 目标
在 Chroma MCP Server 中添加 `chroma_generate_keywords` 工具，利用 K-Means 聚类算法分析集合中的向量，并结合 TextRank 算法提取具有代表性的关键词。

## 技术方案
基于用户提供的“方案二：基于向量聚类的方案”。

### 1. 依赖管理 (`pyproject.toml`)
需要添加以下 Python 库支持：
- `scikit-learn`: 用于 K-Means 聚类算法。
- `jieba`: 用于中文分词和 TextRank 关键词提取。
- `numpy`: 用于向量矩阵操作（`chromadb` 已依赖，但显式声明更佳）。

### 2. 代码实现 (`src/chroma_mcp/server.py`)
新增工具函数 `chroma_generate_keywords`：

**输入参数**:
- `collection_name` (str): 集合名称。
- `n_clusters` (int, default=10): 聚类数量（主题数）。
- `top_k_per_cluster` (int, default=5): 每个聚类提取的关键词数量。

**核心逻辑**:
1.  **获取数据**: 使用 `collection.get(include=['embeddings', 'documents'])` 获取集合内所有向量和文档。
2.  **数据校验**:
    - 检查集合是否为空。
    - 如果文档数量少于 `n_clusters`，自动调整聚类数量为文档总数，避免报错。
3.  **聚类 (Clustering)**:
    - 使用 `sklearn.cluster.KMeans` 对 `embeddings` 进行聚类。
4.  **关键词提取 (Extraction)**:
    - 遍历每个簇 (Cluster)。
    - 将该簇内的所有文档文本拼接。
    - 使用 `jieba.analyse.textrank` 提取 Top K 关键词。
5.  **汇总**:
    - 合并所有簇的关键词并去重。
    - 返回最终列表。

### 3. 验证计划
创建测试脚本 `test_keywords.py`：
- 连接到现有的 `techChat` 集合（或其他由 E2E 测试创建的集合）。
- 调用 `chroma_generate_keywords`。
- 打印生成的关键词，验证输出合理性。

## 执行步骤
1.  **Switch to Code Mode**: 切换模式进行代码修改。
2.  **Update Dependencies**: 修改 `pyproject.toml` 添加依赖。
3.  **Implement Tool**: 修改 `src/chroma_mcp/server.py` 实现功能。
4.  **Verify**: 运行测试脚本验证结果。