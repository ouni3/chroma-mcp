# 计划：添加真实嵌入模型集成测试

## 目标
创建一套自动化集成测试，用于验证 Chroma MCP Server 与真实嵌入模型（如 Gemini）和 Chroma 数据库的端到端交互。

## 待办事项 (Todo List)

- [ ] **创建集成测试文件** (`tests/test_integration_real.py`)
    - [ ] 配置测试环境以加载 `.env` 文件中的真实 API 密钥。
    - [ ] 定义 `pytest.mark.integration` 标记，以便在普通单元测试中默认跳过。
- [ ] **实现真实嵌入生成测试**
    - [ ] 调用 `chroma_embed_texts` 工具。
    - [ ] 验证返回的向量维度是否符合预期（例如 Gemini 为 3072 维，而不是 Mock 的 384 维）。
- [ ] **实现端到端 RAG 流程测试**
    - [ ] 创建临时测试集合。
    - [ ] 添加示例文档（触发真实嵌入）。
    - [ ] 执行语义查询（`chroma_query_documents`）。
    - [ ] 验证查询结果的相关性或存在性。
    - [ ] 清理测试数据。
- [ ] **配置 Pytest**
    - [ ] 更新 `pyproject.toml` 或 `pytest.ini` 注册自定义标记。
- [ ] **更新文档**
    - [ ] 在 `README.md` 中说明如何运行集成测试（例如 `pytest -m integration`）。