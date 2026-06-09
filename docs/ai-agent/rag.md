- RAG（检索增强生成）

  ## 一、核心思想

  解决LLM知识不更新问题：

  > 检索 + 生成

  ---

  ## 二、流程

  1. 文档切分
  2. 向量化（Embedding）
  3. 存入向量库
  4. 查询匹配
  5. LLM生成回答

  ---

  ## 三、关键组件

  - Embedding模型
  - Vector DB（Milvus / FAISS）
  - Retriever
  - LLM

  ---

  ## 四、工程价值

  - 企业知识库
  - 智能客服
  - 内部问答系统