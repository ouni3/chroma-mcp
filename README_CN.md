<p align="center">
  <a href="https://trychroma.com"><img src="https://user-images.githubusercontent.com/891664/227103090-6624bf7d-9524-4e05-9d2c-c28d5d451481.png" alt="Chroma logo"></a>
</p>

<p align="center">
    <b>Chroma - 开源嵌入数据库</b>. <br />
    构建具有记忆功能的 Python 或 JavaScript LLM 应用的最快方式！
</p>

<p align="center">
  <a href="https://discord.gg/MMeYNTmh3x" target="_blank">
      <img src="https://img.shields.io/discord/1073293645303795742?cacheSeconds=3600" alt="Discord">
  </a> |
  <a href="https://github.com/chroma-core/chroma/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/static/v1?label=license&message=Apache 2.0&color=white" alt="License">
  </a> |
  <a href="https://docs.trychroma.com/" target="_blank">
      文档
  </a> |
  <a href="https://www.trychroma.com/" target="_blank">
      主页
  </a>
</p>

# Chroma MCP 服务器

[![smithery badge](https://smithery.ai/badge/@chroma-core/chroma-mcp)](https://smithery.ai/server/@chroma-core/chroma-mcp)

[模型上下文协议 (MCP)](https://modelcontextprotocol.io/introduction) 是一个开放协议，旨在实现 LLM 应用程序与外部数据源或工具之间的轻松集成，提供了一个标准化的框架，以便无缝地为 LLM 提供所需的上下文。

此服务器提供由 Chroma 支持的数据检索功能，使 AI 模型能够基于生成的数据和用户输入创建集合，并使用向量搜索、全文搜索、元数据过滤等方式检索该数据。

这是一个用于自托管 Chroma 访问的 MCP 服务器。如果您正在寻找 [包搜索 (Package Search)](https://www.trychroma.com/package-search)，可以在[这里](https://github.com/chroma-core/package-search)找到相关仓库。

## 特性

- **灵活的客户端类型**
  - Ephemeral (临时/内存中)：用于测试和开发
  - Persistent (持久化)：用于基于文件的存储
  - HTTP 客户端：用于自托管的 Chroma 实例
  - Cloud 客户端：用于 Chroma Cloud 集成（自动连接到 api.trychroma.com）

- **集合管理**
  - 创建、修改和删除集合
  - 分页列出所有集合
  - 获取集合信息和统计数据
  - 配置 HNSW 参数以优化向量搜索
  - 创建集合时选择嵌入函数

- **文档操作**
  - 添加带有可选元数据和自定义 ID 的文档
  - 使用语义搜索查询文档
  - 使用元数据和文档内容进行高级过滤
  - 通过 ID 或过滤器检索文档
  - 全文搜索功能

### 支持的工具

- `chroma_list_collections` - 分页列出所有集合
- `chroma_create_collection` - 创建具有可选 HNSW 配置的新集合
- `chroma_peek_collection` - 查看集合中的文档示例
- `chroma_get_collection_info` - 获取有关集合的详细信息
- `chroma_get_collection_count` - 获取集合中的文档数量
- `chroma_modify_collection` - 更新集合的名称或元数据
- `chroma_delete_collection` - 删除集合
- `chroma_add_documents` - 添加带有可选元数据和自定义 ID 的文档
- `chroma_query_documents` - 使用具有高级过滤的语义搜索查询文档
- `chroma_get_documents` - 通过 ID 或过滤器分页检索文档
- `chroma_update_documents` - 更新现有文档的内容、元数据或嵌入
- `chroma_delete_documents` - 从集合中删除特定文档

### 嵌入函数
Chroma MCP 支持多种嵌入函数：`default`（默认）、`cohere`、`openai`、`jina`、`voyageai` 和 `roboflow`。

嵌入函数利用 Chroma 的集合配置，该配置会持久化集合所选的嵌入函数以便检索。一旦使用集合配置创建了集合，在未来的查询和插入检索时，将使用相同的嵌入函数，而无需再次指定。嵌入函数持久化是在 Chroma v1.0.0 中添加的，因此如果您使用 <=0.6.3 版本创建了集合，则不支持此功能。

当访问使用外部 API 的嵌入函数时，请确保添加格式正确的 API 密钥环境变量，详见 [嵌入函数环境变量](#嵌入函数环境变量)。

## 在 Claude Desktop 中使用

1. 要添加临时客户端，请将以下内容添加到您的 `claude_desktop_config.json` 文件中：

```json
"chroma": {
    "command": "uvx",
    "args": [
        "chroma-mcp"
    ]
}
```

2. 要添加持久化客户端，请将以下内容添加到您的 `claude_desktop_config.json` 文件中：

```json
"chroma": {
    "command": "uvx",
    "args": [
        "chroma-mcp",
        "--client-type",
        "persistent",
        "--data-dir",
        "/full/path/to/your/data/directory"
    ]
}
```

这将创建一个使用指定数据目录的持久化客户端。

3. 要连接到 Chroma Cloud，请将以下内容添加到您的 `claude_desktop_config.json` 文件中：

```json
"chroma": {
    "command": "uvx",
    "args": [
        "chroma-mcp",
        "--client-type",
        "cloud",
        "--tenant",
        "your-tenant-id",
        "--database",
        "your-database-name",
        "--api-key",
        "your-api-key"
    ]
}
```

这将创建一个云客户端，自动使用 SSL 连接到 api.trychroma.com。

**注意：** 在本地设备上，直接在参数中添加 API 密钥是可以的，但为了安全起见，您也可以在 `args` 列表中使用 `--dotenv-path` 参数指定环境配置文件的自定义路径，例如：`"args": ["chroma-mcp", "--dotenv-path", "/custom/path/.env"]`。

4. 要连接到 [您自己的云提供商上的自托管 Chroma 实例](https://docs.trychroma.com/production/deployment)，请将以下内容添加到您的 `claude_desktop_config.json` 文件中：

```json
"chroma": {
    "command": "uvx",
    "args": [
      "chroma-mcp", 
      "--client-type", 
      "http", 
      "--host", 
      "your-host", 
      "--port", 
      "your-port", 
      "--custom-auth-credentials",
      "your-custom-auth-credentials",
      "--ssl",
      "true"
    ]
}
```

这将创建一个连接到您自托管 Chroma 实例的 HTTP 客户端。

### 演示

在 [Chroma MCP 文档](https://docs.trychroma.com/integrations/frameworks/anthropic-mcp#using-chroma-with-claude) 中查找参考用法，例如共享知识库和向上下文窗口添加记忆。

### 使用环境变量

您还可以使用环境变量来配置客户端。服务器将自动从 `--dotenv-path` 指定路径（默认为工作目录中的 `.chroma_env`）下的 `.env` 文件或系统环境变量中加载变量。命令行参数优先于环境变量。

```bash
# 通用变量
export CHROMA_CLIENT_TYPE="http"  # 或 "cloud", "persistent", "ephemeral"

# 用于持久化客户端
export CHROMA_DATA_DIR="/full/path/to/your/data/directory"

# 用于云客户端 (Chroma Cloud)
export CHROMA_TENANT="your-tenant-id"
export CHROMA_DATABASE="your-database-name"
export CHROMA_API_KEY="your-api-key"

# 用于 HTTP 客户端 (自托管)
export CHROMA_HOST="your-host"
export CHROMA_PORT="your-port"
export CHROMA_CUSTOM_AUTH_CREDENTIALS="your-custom-auth-credentials"
export CHROMA_SSL="true"

# 可选：指定 .env 文件的路径 (默认为 .chroma_env)
export CHROMA_DOTENV_PATH="/path/to/your/.env" 
```

#### 嵌入函数环境变量
当使用访问 API 密钥的外部嵌入函数时，请遵循命名约定 `CHROMA_<>_API_KEY="<key>"`。
因此，要设置 Cohere API 密钥，请设置环境变量 `CHROMA_COHERE_API_KEY=""`。我们建议将其添加到某个位置的 .env 文件中，并使用 `CHROMA_DOTENV_PATH` 环境变量或 `--dotenv-path` 标志来设置该位置以便妥善保存。