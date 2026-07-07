# Claude Code Skills

> Skills 是 Claude Code 的技能系统，本质是一组结构化的指令和资源文件，赋予 Claude 执行特定任务的上下文能力。每个 Skill 包含核心指令、脚本、参考文档和资源模板。

---

## 一、Skills 概述

### 1. 什么是 Skill？

Skill = **结构化指令包**，在对话时注入到 System Prompt 中，让 Claude 获得特定领域的上下文和工具。

```
用户输入 → Claude Code
               │
       Skill 加载机制
           │
   ┌───────┴───────┐
   │               │
   SKILL.md       scripts/    references/    assets/
   (核心指令)      (可执行脚本)  (知识参考)      (模板/资源)
   │               │
   └───────┬───────┘
           │
   注入 System Prompt
           │
   Claude 获得技能上下文 → 执行任务
```

### 2. Skill 的目录结构

```
skill-name/
├── SKILL.md           # 核心指令文件（必需）
├── scripts/           # 可执行脚本（可选）
│   ├── init.sh
│   └── verify.sh
├── references/        # 参考文档（可选）
│   ├── api-spec.md
│   └── config-template.yaml
└── assets/            # 模板和资源文件（可选）
    ├── templates/
    └── images/
```

| 文件/目录 | 必需 | 说明 |
|-----------|------|------|
| **SKILL.md** | ✅ | 核心指令文件，定义技能的全部行为逻辑 |
| **scripts/** | ❌ | 可执行的 shell 脚本，用于执行自动化任务 |
| **references/** | ❌ | 参考文档、API 规范、配置说明等辅助知识 |
| **assets/** | ❌ | 模板文件、图片等静态资源 |

---

## 二、SKILL.md 核心指令文件

### 1. 文件定位与作用

`SKILL.md` 是技能的**核心入口**，当 Skill 被加载时，其内容直接注入到对话的 System Prompt 中。它定义了：
- 技能的目标和能力范围
- 行为规则与约束
- 可用工具和脚本
- 工作流程

### 2. 标准结构

```markdown
# <技能名称>

<技能的一句话描述>

## 概述

<技能的详细说明，包括能力边界、适用场景>

## 规则

<行为规则列表，定义 Claude 在执行该技能时应遵守的约束>

## 工作流程

<定义技能的步骤化执行流程>

## 可用脚本

<列出 scripts/ 目录下的可用脚本及其用途>

## 参考文档

<列出 references/ 目录下的参考文档及其用途>
```

### 3. 完整示例

```markdown
# Git 工作流技能

协助完成 Git 仓库的日常管理、代码审查和发布流程。

## 概述

本技能涵盖 Git 分支管理、提交规范、代码审查流程和发布管理。
支持 GitHub/GitLab 工作流。

## 规则

1. 提交信息遵循 Conventional Commits 规范
2. 在修改代码前先检查当前分支状态
3. 重要操作（rebase、force push）前先与用户确认
4. 合并请求前确保 CI 通过

## 工作流程

### 1. 代码审查流程
1. 获取目标分支的变更列表：`git diff main...HEAD --stat`
2. 逐文件审查变更内容
3. 检查提交信息是否符合规范
4. 汇总审查意见

### 2. 发布流程
1. 确认当前分支和未合并的 PR
2. 运行完整测试套件
3. 根据版本号更新 CHANGELOG
4. 创建版本标签

## 可用脚本

- `scripts/prepare-commit.sh` — 自动格式化并检查提交信息
- `scripts/release.sh` — 自动化发布流程

## 参考文档

- `references/commit-convention.md` — 提交规范详细说明
- `references/release-checklist.md` — 发布检查清单
```

---

## 三、三层加载机制

Skills 采用**三层叠加加载**机制，优先级从高到低依次为：

```
                   用户级 (~/.claude/skills/)
                          ↑ 覆盖
                  项目级 (.claude/skills/)
                          ↑ 覆盖
                  内置级 (Claude Code 自带)
```

### 1. 三层说明

| 层级 | 路径 | 所有者 | 优先级 | 说明 |
|------|------|--------|--------|------|
| **内置级** | Claude Code 安装目录 | Claude Code | 最低 | 官方预装技能，不可修改 |
| **项目级** | `.claude/skills/` | 项目维护者 | 中 | 团队成员共享，随项目版本管理 |
| **用户级** | `~/.claude/skills/` | 用户 | **最高** | 个人自定义技能，覆盖前两级 |

### 2. 加载机制

```
Claude Code 启动
        │
        ▼
扫描三层 Skill 目录
        │
        ▼
同一 Skill 名 → 优先级高覆盖优先级低（用户级 > 项目级 > 内置级）
        │
        ▼
全文加载 SKILL.md → 注入 System Prompt
        │
        ▼
注册 scripts/ 为可用工具
        │
        ▼
references/ 和 assets/ 按需提供
```

```yaml
# 覆盖规则示例
内置级：claude-code/skills/git-workflow/SKILL.md       # 基础版本
项目级：.claude/skills/git-workflow/SKILL.md            # 覆盖：加入团队规范
用户级：~/.claude/skills/git-workflow/SKILL.md          # 覆盖：加入个人偏好
# 最终生效：用户级 SKILL.md
```

### 3. 同名 Skill 覆盖行为

| 场景 | 行为 | 说明 |
|------|------|------|
| 三层同名 | 用户级完全替代内置级 | 适合完全自定义 |
| 只覆盖部分字段 | 整文件替换，无法部分合并 | SKILL.md 是整体覆盖 |
| 新增 skill | 无冲突，三层合并 | 不同名的 skill 共存 |

::: tip 推荐实践
- **项目级 Skill** 放置团队共用的工作流规范（占 90% 场景）
- **用户级 Skill** 仅放个人偏好（如编辑器快捷键、个人模板）
- **不要修改内置 Skill**——更新 Claude Code 时会被覆盖
- **SKILL.md 是整体覆盖**，无法逐行合并，想保留内置内容需要手动复制
:::

---

## 四、scripts/ 目录：可执行脚本

### 1. 作用与加载

`scripts/` 目录下的脚本被注册为 Claude 可调用的工具，Claude 可以在对话中主动执行这些脚本。

```
skill-name/scripts/
├── init.sh          # 初始化环境
├── verify.sh        # 验证结果
├── format.sh        # 格式化代码
└── deploy.sh        # 部署应用
```

### 2. 脚本要求

```bash
#!/bin/bash
# scripts/verify.sh —— 代码验证脚本
# 要求：
# 1. 第一行 shebang（#!/bin/bash 或 #!/usr/bin/env node）
# 2. 可执行权限（chmod +x）
# 3. 良好的退出码（0=成功，非0=失败）
# 4. 输出到 stdout/stderr

set -euo pipefail

echo "Running verification..."
# 验证逻辑
if [ $? -eq 0 ]; then
    echo "✅ Verification passed"
    exit 0
else
    echo "❌ Verification failed"
    exit 1
fi
```

```bash
# 设置执行权限
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### 3. 脚本类型

| 脚本类型 | 语言 | 适用场景 |
|---------|------|---------|
| **Shell 脚本** | `#!/bin/bash` | 文件操作、命令编排、开发环境管理 |
| **Python 脚本** | `#!/usr/bin/env python3` | 数据处理、API 调用、复杂逻辑 |
| **Node 脚本** | `#!/usr/bin/env node` | 前端工具链、JavaScript 生态 |
| **Makefile** | 直接调用 make | 构建、测试任务 |

### 4. 脚本编写规范

```bash
#!/bin/bash
# ======================================
# scripts/deploy.sh
# 功能：自动化部署到测试环境
# 用法：./deploy.sh <environment> [version]
# 参数：
#   environment - 目标环境（staging/production）
#   version    - 可选，发布的版本号
# 依赖：kubectl, helm
# ======================================

set -euo pipefail

ENVIRONMENT="${1:-}"
VERSION="${2:-latest}"

if [ -z "$ENVIRONMENT" ]; then
    echo "错误：请指定部署环境"
    echo "用法：$0 <environment> [version]"
    exit 1
fi

echo "部署 $VERSION 到 $ENVIRONMENT 环境..."
# 部署逻辑
echo "✅ 部署完成"
```

::: warning 脚本安全注意事项
- **不要硬编码密钥**——使用环境变量或密钥管理服务
- **确认破坏性操作**——删除/覆盖前输出提示并与用户确认
- **退出码规范**——成功 0，失败非 0
- **输出规范**——关键信息输出到 stdout，错误输出到 stderr
:::

---

## 五、references/ 目录：参考文档

### 1. 作用

`references/` 目录存放技能执行时需要的参考知识，Claude 在执行任务时可以根据需要查阅这些文档。

```
skill-name/references/
├── api-spec.md              # API 规范文档
├── coding-standards.md      # 编码规范
├── architecture.md          # 架构说明
├── changelog-template.md    # CHANGELOG 模板
└── images/
    └── architecture.png     # 架构图
```

### 2. 文档类型

| 文档 | 格式 | 用途 |
|------|------|------|
| **编码规范** | Markdown | 定义代码风格、命名规范、项目约定 |
| **API 文档** | Markdown/OpenAPI | API 接口规范、参数说明、示例 |
| **架构文档** | Markdown | 系统架构说明、模块关系 |
| **模板文件** | Markdown | 提交信息模板、PR 模板、CHANGELOG 模板 |
| **配置说明** | YAML/JSON | 环境配置参考、参数说明 |

### 3. 编写示例

```markdown
# references/coding-standards.md

## Java 编码规范

### 命名规范
- 类名：UpperCamelCase，如 `UserService`
- 方法名：lowerCamelCase，如 `findUserById`
- 常量：UPPER_SNAKE_CASE，如 `MAX_RETRY_COUNT`

### 代码格式
- 缩进：4 个空格
- 最大行宽：120 字符
- 文件末尾保留一个空行

### 异常处理
- 不要 catch 后吞掉异常
- 业务异常使用 BizException 而非 RuntimeException
- 资源操作使用 try-with-resources
```

---

## 六、assets/ 目录：模板和资源文件

### 1. 作用

`assets/` 目录存放技能的模板文件、图片等静态资源，在技能执行时可以读取和引用。

```
skill-name/assets/
├── templates/
│   ├── pr-template.md        # PR 模板
│   ├── commit-template.md    # 提交信息模板
│   └── changelog-template.md # CHANGELOG 模板
└── images/
    └── workflow.png          # 工作流说明图
```

### 2. 模板文件示例

```markdown
# assets/templates/pr-template.md

## 变更说明

<!-- 简要描述本次 PR 的变更内容 -->

## 变更类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 依赖升级

## 测试

- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 手动验证完成

## 检查清单

- [ ] 代码符合项目编码规范
- [ ] 已添加/更新相关文档
- [ ] 无遗留的调试代码或注释
```

---

## 七、Skill 开发实战

### 1. 项目级 Skill 推荐目录结构

```
.claude/skills/${skill-name}/
├── SKILL.md              # 技能核心指令（必需）
├── scripts/              # 可执行脚本
│   ├── init.sh
│   └── verify.sh
├── references/           # 参考文档
│   └── coding-standards.md
└── assets/               # 模板资源
    └── templates/
        └── pr-template.md
```

### 2. 完整示例：代码审查技能

```markdown
# .claude/skills/code-review/SKILL.md

# Code Review 技能

协助完成代码审查，确保代码质量、安全性和可维护性。

## 概述

本技能适用于代码审查场景，支持 Java、Python、JavaScript、Go 等语言。
会在提交 PR 或请求审查时自动激活。

## 规则

1. 先了解整体变更范围，再逐文件审查
2. 每条审查意见必须指出代码位置（文件+行号）
3. 区分严重程度：blocker / major / minor / suggestion
4. 对 blocker 级别的问题给出具体的修复建议和代码示例
5. 保持专业友善的语气
6. 如果发现安全漏洞，优先报告而非公开评论

## 工作流程

### 审查步骤
1. 运行 `scripts/pre-review.sh` 获取变更概览
2. 逐文件审查变更内容，关注：
   - 安全性：SQL 注入、XSS、敏感信息泄露
   - 性能：不必要的循环、N+1 查询、内存泄漏
   - 可维护性：命名、注释、设计模式
3. 运行 `scripts/run-check.sh` 执行静态分析
4. 汇总审查意见

## 可用脚本

- `scripts/pre-review.sh` — 获取变更概览和 diff 统计
- `scripts/run-check.sh` — 运行静态代码分析工具

## 参考文档

- `references/coding-standards.md` — 项目编码规范
- `references/security-checklist.md` — 安全检查清单
```

```bash
#!/bin/bash
# scripts/pre-review.sh
# 代码审查前置脚本：获取变更概览

set -euo pipefail

echo "=== 变更概览 ==="
git diff main...HEAD --stat

echo ""
echo "=== 新增代码行数 ==="
git diff main...HEAD --shortstat

echo ""
echo "=== 变更文件列表 ==="
git diff main...HEAD --name-only
```

### 3. 加载与激活

Skill 在 Claude Code 启动时自动加载，无需手动操作。

```bash
# 查看当前已加载的 Skills
# Claude Code CLI 中运行：
/claude-skills list

# 或者某个 skill 是否生效，直接在对话中测试
/代码审查   # 如果 code-review skill 已加载，会激活对应行为
```

::: tip Skill 激活方式
- **自动匹配**：Claude 根据用户输入自动选择匹配的 Skill 激活
- **命令触发**：通过 `/` 命令前缀显式触发
- **上下文推断**：Claude 读取 SKILL.md 后，在相关上下文中自行判断是否应用指令
:::

---

## 八、常见踩坑与最佳实践

### 1. 编写反模式

::: danger SKILL.md 常见错误

| # | 反模式 | 问题 | 正确做法 |
|---|-------|------|---------|
| 1 | **指令过于模糊** | Claude 不知道具体该怎么做 | 给出明确步骤和检查清单 |
| 2 | **规则过于冗长** | 超出上下文窗口，核心规则被稀释 | 精炼到关键规则，长篇参考放 references/ |
| 3 | **SKILL.md 包含太多代码** | 浪费上下文空间 | 关键示例保留，完整代码放 references/ |
| 4 | **脚本无错误处理** | 执行失败时无反馈 | 完善退出码、错误信息输出 |
| 5 | **忽略三层覆盖机制** | 项目级修改用户级不生效 | 理解覆盖规则，选择正确的层级放置 |
| 6 | **硬编码路径** | 项目迁移后失效 | 使用相对路径，或通过脚本动态获取 |
| 7 | **缺少 shebang 或执行权限** | 脚本不可执行 | `#!/bin/bash` + `chmod +x` |
| 8 | **SKILL.md 版本未纳入版本控制** | 团队无法共享 | 项目级 Skill 随代码仓库一起管理 |

```markdown
# ❌ 反模式：过于模糊
帮助团队进行代码审查

# ✅ 正确：明确的范围和步骤
## 工作流程
1. 运行 pre-review.sh 获取变更概览
2. 从安全性、性能、可维护性三个维度逐文件审查
3. 每条意见标注 blocker/major/minor/suggestion
4. 汇总输出审查报告
```
:::

### 2. 最佳实践

| 实践 | 说明 |
|------|------|
| **Skill 粒度适中** | 一个 Skill 对应一个任务域，不要太大也不要太碎 |
| **SKILL.md 控制在 2-3 屏** | 过长会占用过多上下文资源 |
| **scripts/ 做自动化** | 把重复性操作写成脚本，SKILL.md 中引用 |
| **references/ 做知识库** | 详细规范、文档放到 references/，SKILL.md 只引用 |
| **项目级 Skill 纳入版本控制** | 团队共享，随代码库更新 |
| **用户级 Skill 放个人偏好** | 编辑器配置、快捷键、个人工作流 |
| **用 `/` 命令设计触发词** | 让用户能直接 `/<skill-name>` 触发 |

### 3. Skill 大小与上下文影响

```yaml
# SKILL.md 大小对上下文的影响
SKILL.md 1KB   → 约占用 250 tokens 上下文
SKILL.md 5KB   → 约占用 1250 tokens 上下文  
SKILL.md 10KB  → 约占用 2500 tokens 上下文

# 建议：
# - 核心指令：SKILL.md ≤ 5KB（聚焦关键规则和流程）
# - 详细内容放 references/（按需查阅，不占用上下文）
```

---

## 九、Skills 使用场景示例

### 1. 项目规范类

```
.claude/skills/project-convention/
├── SKILL.md                # 项目规范总纲领
├── references/
│   ├── commit-convention.md  # 提交规范
│   └── branch-naming.md     # 分支命名规范
└── scripts/
    └── validate-commit.sh    # 提交信息校验
```

### 2. 部署类

```
.claude/skills/deployment/
├── SKILL.md                # 部署流程说明
├── scripts/
│   ├── build.sh
│   ├── test.sh
│   └── rollback.sh
└── references/
    └── infrastructure.md   # 基础设施说明
```

### 3. 测试类

```
.claude/skills/testing/
├── SKILL.md                # 测试策略与规范
├── references/
│   └── test-strategy.md    # 测试策略详细文档
└── scripts/
    ├── run-unit-tests.sh
    └── run-integration-tests.sh
```

---

## 十、面试高频问题

### Q1：Claude Code Skills 是什么？目录结构是怎样的？

**答**：
Skills 是 Claude Code 的技能系统，通过结构化的指令文件让 Claude 获得特定任务域的上下文能力。标准目录结构为：

```
skill-name/
├── SKILL.md        # 核心指令（注入 System Prompt）
├── scripts/        # 可执行脚本
├── references/     # 参考文档
└── assets/         # 模板资源
```

`SKILL.md` 是必需的核心文件，其余目录为可选。

### Q2：三层加载机制是怎样的？

**答**：
Skills 有三层由低到高的优先级：
1. **内置级**（Claude Code 自带）— 不可修改，优先级最低
2. **项目级**（`.claude/skills/`）— 随项目版本管理，团队共享
3. **用户级**（`~/.claude/skills/`）— 个人自定义，**优先级最高**

同名 Skill 会**整体覆盖**（非逐行合并），高优先级层替换低优先级层的完整 SKILL.md。

### Q3：SKILL.md 应该包含哪些内容？

**答**：
一个标准的 SKILL.md 包含：
- 技能名称和一句话描述
- 概述（详细说明能力范围）
- 规则列表（行为约束）
- 工作流程（步骤化的执行流程）
- 可用脚本列表（scripts/ 目录中的脚本说明）
- 参考文档索引（references/ 目录中的文档说明）

建议控制在 5KB 以内，以避免占用过多上下文窗口。

### Q4：scripts/ 目录有什么特殊要求？

**答**：
- 脚本必须具有 shebang（`#!/bin/bash` 等）
- 必须是可执行文件权限（`chmod +x`）
- 退出码规范（0 成功，非 0 失败）
- 不要硬编码密钥
- 破坏性操作前提示确认

这些脚本会在 Skill 加载时注册为 Claude 可调用的工具。

### Q5：项目级 Skill 和用户级 Skill 怎么选择？

**答**：
- **项目级**（`.claude/skills/`）：团队共用的规范、流程、配置，随代码仓库版本管理。占实际使用的 90%。
- **用户级**（`~/.claude/skills/`）：仅与个人相关的偏好设置（编辑器快捷键、个人工作流）。想覆盖或自定义项目级 / 内置级行为时使用。

建议将项目级 Skill 纳入 Git 管理，让整个团队共享。

---

---

## 十一、优秀 Skills 资源推荐

> ⚠️ **说明**：以下数据基于 2026 年 7 月的公开信息。GitHub 上已有 **1400+** 个 Claude Code Skills 仓库，但真正值得装的**不超过 10 个**。以下只列出经过社区验证、有明确 Star 数据的高质量资源。

### 1. 🏆 三大顶流（社区公认必装）

这三个仓库代表了 Skills 生态的三种不同哲学，是目前 Star 最高、社区讨论最广的选择。

| 仓库 | ⭐ (2026.07) | 哲学 | 一句话 |
|------|-------------|------|--------|
| **obra/superpowers** | ~200k | **纪律** — 强制工作流 | 14 个核心 Skill，涵盖 TDD、代码审查、并行 Agent、Git 工作流 |
| **anthropics/skills** | ~155k | **官方标准** — 参考实现 | Anthropic 官方维护，文档处理、设计、Canvas 等 |
| **mattpocock/skills** | ~100k | **工具** — 按需触发 | TypeScript 教父出品，28 个 Skill 涵盖工程和效率 |

**三者定位对比**：superpowers 是"框架"（改变工作方式），anthropics/skills 是"标准库"（官方能力），mattpocock/skills 是"工具箱"（按需调用）。

#### obra/superpowers（v5.1.0）

14 个核心 Skill 分三类：

| 类别 | Skills |
|------|--------|
| **开发工作流** | brainstorming、writing-plans、executing-plans、subagent-driven-development、using-git-worktrees、finishing-a-development-branch |
| **质量保证** | test-driven-development、requesting-code-review、receiving-code-review、verification-before-completion |
| **调试与元技能** | systematic-debugging、writing-skills、using-superpowers、dispatching-parallel-agents |

**安装**：
```bash
npx skills add obra/superpowers
```
**适合**：团队需要强制工程规范、复杂多文件项目。**不适合**：快速原型、单文件脚本。

#### anthropics/skills — 官方标准库

| 类别 | Skills |
|------|--------|
| **文档处理** | create-docx（Word）、create-pptx（PPT）、create-pdf、create-xlsx（Excel） |
| **设计** | frontend-design（UI 设计质量提升）、build-canvas（Mermaid/Excalidraw 图表） |
| **开发** | mcp-builder（MCP Server 构建）、github-mcp-server（GitHub 集成） |

#### mattpocock/skills — TypeScript 教父的工具箱

| 类别 | Skills |
|------|--------|
| **工程** | tdd、diagnose（调试）、improve-codebase-architecture（架构改进）、grill-with-docs（需求反诘）、triage、prototype、zoom-out |
| **效率** | caveman（Token 压缩 ~75%）、handoff（上下文交接）、grill-me、write-a-skill |
| **安全** | git-guardrails（防止危险 Git 命令） |

### 2. 📦 精选 Awesome Lists（合集索引）

| 资源 | ⭐ | 特点 |
|------|----|------|
| **[onmyway133/awesome-claude-code](https://github.com/onmyway133/awesome-claude-code)** | 高星 | 精选高质量工具，200+ star 门槛过滤 |
| **[subinium/awesome-claude-code](https://github.com/subinium/awesome-claude-code)** | — | 涵盖 Claude Code / Codex / Gemini CLI / Cursor |
| **[Chat2AnyLLM/awesome-claude-skills](https://github.com/Chat2AnyLLM/awesome-claude-skills)** | — | 元数据索引，追踪 **58,000+ Skills** 来源，458 个源头仓库 |
| **[helloianneo/awesome-claude-code-skills](https://github.com/helloianneo/awesome-claude-code-skills)** | — | **中文精选**，50+ Skills 按场景分类带推荐等级，每项有安装命令 |
| **[Smaiil/awesome-claude-agents](https://github.com/Smaiil/awesome-claude-agents)** | — | 100+ 生产级 Agent + 80+ Skills，覆盖 **Java/Go/Rust/Python/TS** 等 |
| **[FridrichMethod/awesome-skills](https://github.com/FridrichMethod/awesome-skills)** | — | **1800+ Skills** 自动同步合集，覆盖 AI4Protein、生物信息学、学术写作 |
| **[the911fund/skill-of-skills](https://github.com/the911fund/skill-of-skills)** | — | 质量排名的 Skill 搜索引擎，930+ Skills |

### 3. 🛠 开发效率类

#### 代码质量与工程化

| 名称 | ⭐ | 功能 |
|------|----|------|
| **superpowers** | ~200k | TDD + 并行 Agent + 代码审查 + Git 工作流（见上文） |
| **mattpocock/skills** | ~100k | tdd、diagnose、architecture-improvement、prototype（见上文） |
| **addyosmani/agent-skills** | ~60k | **Google 工程实践编码**，23 个 Skill 覆盖完整开发生命周期（spec/plan/build/test/review/ship） |
| **intellectronica/agent-skills** | ⭐ | 内置 **context7**（实时 API 文档查询）和 **claude-mem**（跨会话记忆） |

安装：
```bash
# Addy Osmani（Google 工程规范）
npx skills add addyosmani/agent-skills

# context7（实时 API 文档查询）
npx skills add intellectronica/agent-skills@context7
```

#### 框架与语言专项

| 名称 | ⭐ | 说明 |
|------|----|------|
| **vercel-labs/agent-skills** | ~27k | Vercel 官方：React 最佳实践、Web 设计指南、agent-browser 等 |
| **vercel-labs/skills** | ~24k | CLI 工具：`npx skills add` 的安装器本身 |
| **supabase/agent-skills** | ~2.3k | Supabase 官方：Postgres 最佳实践、数据库 Schema、RLS 策略 |
| **Smaiil/awesome-claude-agents** | — | 多语言框架覆盖面最广（Java/Spring Boot、Python/FastAPI、Go、Rust 等） |

#### 国内开发者资源

| 名称 | 说明 | 链接 |
|------|------|------|
| **helloianneo/awesome-claude-code-skills** | **中文精选**，50+ Skill 带推荐等级和安装命令 | [GitHub](https://github.com/helloianneo/awesome-claude-code-skills) |
| **laolaoshiren/claude-code-skills-zh** | 中文精选 100+ Skills，含 18 个原创可安装技能 | [GitHub](https://github.com/laolaoshiren/claude-code-skills-zh) |

### 4. 📄 办公提效类

#### Anthropic 官方文档处理套件

```bash
npx skills add anthropics/skills@create-docx        # Word 文档
npx skills add anthropics/skills@create-pptx        # PPT 演示文稿
npx skills add anthropics/skills@create-pdf         # PDF
npx skills add anthropics/skills@create-xlsx        # Excel 表格
npx skills add anthropics/skills@create-diagram     # 图表绘制
npx skills add anthropics/skills@build-canvas       # Mermaid/Excalidraw 流程图
```

#### 项目管理与协作

| 名称 | 功能 | 来源 |
|------|------|------|
| **context7** | 实时拉取 API 文档到上下文 | intellectronica/agent-skills |
| **claude-mem** | 跨会话记忆，无需反复交代背景 | intellectronica/agent-skills |
| **handoff** (mattpocock) | 将当前上下文压缩为交接文档 | mattpocock/skills |
| **frontend-design** | 让 AI 生成的 UI 不再千篇一律 | anthropics/skills |

### 5. 🏛 官方资源

| 资源 | ⭐ | 说明 | 链接 |
|------|----|------|------|
| **anthropics/skills** | ~155k | 官方 Skill 仓库 | [GitHub](https://github.com/anthropics/skills) |
| **anthropics/claude-code** | ~135k | Claude Code 官方 CLI 仓库 | [GitHub](https://github.com/anthropics/claude-code) |
| **anthropics/claude-plugins-official** | ~30k | 官方插件目录 | [GitHub](https://github.com/anthropics/claude-plugins-official) |

### 6. 🔒 安全与专业领域

| 名称 | ⭐ | 功能 | 来源 |
|------|----|------|------|
| **trailofbits/skills** | ~5.5k | **安全审计专用**：differential-review、variant-analysis、static-analysis、supply-chain-risk-auditor | Trail of Bits（顶级安全公司） |
| **K-Dense-AI/claude-scientific-skills** | ~23k | **科学计算**：137 个 Skills，支持生物信息学、化学信息学 | 社区 |

### 7. 安装方式速查

```bash
# 方式1：通过 npx skills 安装（推荐，自动管理）
npx skills add obra/superpowers
npx skills add anthropics/skills@frontend-design
npx skills add mattpocock/skills
npx skills add addyosmani/agent-skills

# 方式2：从 vercel-labs/skills 市场安装
npx skills add vercel-labs/agent-skills@agent-browser

# 方式3：手动克隆到项目 Skills 目录（团队共享）
git clone https://github.com/obra/superpowers.git .claude/skills/superpowers

# 方式4：克隆到用户级目录（个人全局可用）
git clone https://github.com/mattpocock/skills.git ~/.claude/skills/mattpocock-skills

# 方式5：查看已安装 Skills
# 在 Claude Code 中运行 /skills list
```

```yaml
# 在 .claude/settings.json 中配置启动时加载的技能
{
  "skills": [
    "obra/superpowers",
    "mattpocock/skills",
    "anthropics/skills"
  ]
}
```

### 8. 选型建议与避坑

#### 新手推荐组合

```bash
# 入门三件套（覆盖 80% 场景）
npx skills add obra/superpowers          # 代码质量 + 工作流
npx skills add anthropics/skills@frontend-design  # 设计质量
npx skills add intellectronica/agent-skills@context7  # API 文档查询

# 前端方向追加
npx skills add vercel-labs/agent-skills@agent-browser  # 浏览器自动化

# 后端方向追加
npx skills add addyosmani/agent-skills   # Google 工程规范
```

#### 场景速查表

| 场景 | 推荐组合 |
|------|---------|
| **新手起步** | superpowers + frontend-design + context7 |
| **前端开发** | + vercel-labs/agent-skills + mattpocock/skills |
| **后端/API 开发** | + addyosmani/agent-skills |
| **文档办公** | + anthropics/skills (docx/pptx/xlsx) |
| **安全审计** | + trailofbits/skills |
| **科学计算** | + K-Dense-AI/claude-scientific-skills |

#### 避坑清单

::: warning 不要装太多
- 每个 Skill 描述约占用 **~100 tokens** 上下文窗口
- 装超过 15 个可能导致部分 Skill 被截断失效
- **社区共识**：真正高频使用的 Skill 不超过 10 个
- 建议先装 3-5 个，用一周再决定哪些保留
:::

| 坑 | 说明 |
|----|------|
| **关注 description 质量** | description 是 LLM 路由 Skill 的依据。好描述说清触发场景，坏描述是营销文案 |
| **检查 SKILL.md 有无分层** | 有 `references/` 子目录说明考虑过 Token 效率，否则 SKILL.md 可能过长 |
| **注意更新频率** | 半年未更新的 Skill 可能已不适用新版 Claude Code |
| **优先官方和顶流** | superpowers / anthropics / mattpocock 三个仓库占总安装量的 80%+ |
| **量力而行** | 不是装得越多越强，精准匹配任务 > 数量堆积 |

---

## 参考文章与推荐阅读

- [Claude Code Skills 官方文档](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code 目录结构说明](https://docs.anthropic.com/en/docs/claude-code/skills#skill-files-and-directory-structure)
- [Skills 三层加载机制](https://docs.anthropic.com/en/docs/claude-code/skills#skill-loading-order)
- [SKILL.md 编写指南](https://docs.anthropic.com/en/docs/claude-code/skills#skill.md-format)
- [Claude Code 项目配置 (.claude/)](https://docs.anthropic.com/en/docs/claude-code/skills#project-skills)

---

## 相关文章

- [LLM 基础](/ai-agent/llm-basic)
- [MCP 协议](/ai-agent/mcp)
