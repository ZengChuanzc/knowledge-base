---
title: Building LLM-as-a-Judge Using Recursive Advisors in Spring AI
date: 2026-07-04
tags: [技术热点]
category: 技术热点
source: Baeldung
author: Ralf Ueberfuhr
---

# Building LLM-as-a-Judge Using Recursive Advisors in Spring AI

## 📝 一句话总结

（暂无）

---

## 📌 核心内容

{
  "title": "🔍 Spring AI 新范式：用 LLM-as-a-Judge 模式构建智能质量门禁，告别盲目输出！",
  "tags": ["Java", "Spring Boot", "Spring AI", "LLM", "AI", "质量门禁"],
  "category": "技术热点",
  "one_sentence": "本文深入解析 Spring AI 中基于 Recursive Advisors 实现 LLM-as-a-Judge 模式，为 LLM 输出搭建自动化质量审核门禁，提升 AI 应用可靠性。",
  "core_content": "## 核心内容\n\n- **LLM-as-a-Judge 模式**：利用大语言模型自身作为评审者，对另一个 LLM 的输出进行质量评估，实现自我纠错与优化。\n- **Recursive Advisors 架构**：Spring AI 提供递归调用机制，将评审逻辑封装为 Advisor，在请求链中递归执行，无需侵入业务代码。\n- **实现步骤**：\n  1. 定义评审标准（如准确性、完整性、一致性）\n  2. 创建 Judge Advisor，接收原始输出并调用评审 LLM\n  3. 配置递归深度与重试策略，避免无限循环\n  4. 集成到 Spring AI 的 ChatClient 或 ChatModel 调用链中\n- **质量门禁效果**：当输出不达标时，自动触发重新生成或降级处理，显著降低幻觉与错误率。\n- **代码示例**：展示如何使用 `RecursiveAdvisor` 接口实现自定义评审逻辑，并与现有 Spring AI 项目无缝集成。",
  "why_worth": "## 为什么值得关注\n\n对于 Java 后端工程师，尤其是正在构建 AI 驱动应用的团队，这篇文章提供了一种可落地的质量保障方案。传统 LLM 应用常面临输出不可控、幻觉频发的问题，而 LLM-as-a-Judge 模式能通过自动化评审显著提升可靠性。Spring AI 作为 Spring 生态中的 AI 集成框架，其 Recursive Advisors 机制让开发者无需深入学习复杂 AI 推理，即可在熟悉的 Spring 编程模型下实现智能质量门禁。这不仅是技术亮点，更是提升 AI 产品生产可用性的关键一步。",
  "tech_highlights": "## 技术亮点\n\n- **新增功能**：Spring AI 的 Recursive Advisors 机制为 LLM 调用链添加了递归评审能力，扩展了 Advisors 模式的应用场景。\n- **架构变化**：将质量门禁从业务逻辑中解耦，通过 Advisor 链式调用实现，保持代码整洁与可维护性。\n- **性能优化**：评审 LLM 通常使用轻量模型（如 GPT-3.5-turbo），避免对主模型性能造成过大影响；支持异步评审与批量处理。\n- **最佳实践**：推荐设置评审深度为 1-2 次，避免过度递归导致成本飙升；评审结果可缓存，提升重复查询效率。\n- **API 变化**：新增 `RecursiveAdvisor` 接口，扩展 `ChatClient` 的 `advisors()` 方法，支持递归配置。\n- **兼容性**：完全兼容 Spring Boot 3.x 与 Spring AI 1.x，无需修改现有业务代码即可集成。",
  "my_thoughts": "## 我的思考\n\n作为一名长期从事 Java 后端开发的工程师，我一直在关注 AI 如何与现有 Spring 生态融合。这篇文章提出的 LLM-as-a-Judge 模式，在我看来是解决 LLM 输出“黑盒”问题的务实之举。\n\n**是否值得学习？** 绝对值得。Spring AI 正在成为 Java 领域 AI 集成的标准框架，掌握 Recursive Advisors 机制能让你在构建 AI 应用时拥有更强的质量控制手段。即使你当前没有直接使用 LLM，理解这种“用 AI 评审 AI”的思路，对设计任何需要自动审核的系统都有启发。\n\n**适用于哪些场景？** 核心场景包括：客服机器人的回答准确性校验、代码生成工具的代码质量检查、内容生成平台的事实核查、以及任何需要保证 LLM 输出可靠性的生产环境。特别适合那些对幻觉容忍度低的金融、医疗、法律等垂直领域。\n\n**未来趋势？** 我认为 LLM-as-a-Judge 模式会逐渐演变为 AI 应用的标准组件，类似现在的日志、缓存、限流。随着多模型协作（MoE）的兴起，评审模型可能会专门优化，甚至出现专用的小型评审模型。Spring AI 的抽象层让

## 💭 我的思考

这种演进对开发者透明。\n\n**是否值得生产环境使用？** 谨慎乐观。当前实现依赖 LLM 的评审能力，而评审模型本身也可能存在偏见或错误。建议搭配人工抽查和统计监控，形成“AI 评审 + 人工兜底”的闭环。另外，递归调用会带来额外的 API 成本和延迟，需要结合业务场景权衡。\n\n**与 Spring AI 的关系？** 非常紧密。这篇文章是 Spring AI 生态的延伸，Recursive Advisors 是其 Advisors 模式的进阶应用。如果你已经在使用 Spring AI 的 ChatClient，集成成本极低；如果还没接触，本文也是一个很好的 Spring AI 实战入门案例。\n\n**是否可以结合 RAG？** 完全可以。RAG（检索增强生成）通过外部知识库提升 LLM 输出质量，而 LLM-as-a-Judge 可以作为 RAG 管道的质量门禁，对检索结果和生成内容进行双重校验。例如，先检索相关文档，再生成回答，然后让 Judge 模型验证回答是否准确引用了文档。这是一个很有前景的组合。\n\n**是否值得后续写专题？** 非常值得。我计划后续深入探索：如何优化评审 prompt 以减少误判、如何实现多维度评审（如安全性、风格一致性）、以及如何将评审结果用于模型微调。这个话题值得一个系列文章。\n\n总之，这篇文章为 Java 开发者提供了一条清晰的路径，让 LLM 应用从“能用”走向“好用”。我强烈建议关注 Spring AI 的读者花时间实践一下，你会对 AI 工程化有更深的理解。"
}

---

> 📎 **原文链接**: [https://feeds.feedblitz.com/~/959091593/0/baeldung~Building-LLMasaJudge-Using-Recursive-Advisors-in-Spring-AI](https://feeds.feedblitz.com/~/959091593/0/baeldung~Building-LLMasaJudge-Using-Recursive-Advisors-in-Spring-AI)

> 📅 **文章日期**: 2026-07-08
> 🏷️ **标签**: 技术热点
> 📂 **分类**: 技术热点
