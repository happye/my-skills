---
name: harness-project-init
description: >-
  新项目初始化的 Harness Engineering 搭建流程。当用户说"新建项目""初始化项目""搭建脚手架""harness""新仓库""project setup""scaffold""开始新项目"时触发。
  基于官方 Harness Engineering 实践 + 真实项目对抗审查提炼的纪律门禁，生成完整工程脚手架：目录结构、多工具配置文件、两层记忆资产（.learnings/ + 工具记忆种子）、工程纪律门禁、用户协作偏好固化。
  覆盖工具：Claude Code (CLAUDE.md)、GitHub Copilot (.github/copilot-instructions.md)、Cursor (.cursor/rules/)、Windsurf (.windsurfrules)、Cline (.clinerules/)、AGENTS.md (通用标准)、Aider (CONVENTIONS.md)、Codex (CODEX.md)、Gemini CLI (GEMINI.md)。
  信源：OpenAI 2026-02-11 Harness Engineering、Anthropic 2025-11-26 Effective harnesses、Anthropic 2026-03-24 Harness design、Anthropic 2026-04-08 Managed Agents、Martin Fowler 2026-04-02 Feedforward/Feedback、agents.md 标准。
---

# Harness Project Init

新项目初始化时，按以下流程执行 Harness Engineering 搭建。

## 触发条件

用户说以下任意关键词时触发本 skill：
- "新建项目""初始化项目""搭建脚手架""harness""新仓库""project setup""scaffold"
- "开始新项目""创建项目配置""Agent配置文件"

## 执行流程

### Step 0: 收集项目信息

向用户询问以下必要信息（缺少的才问，已有的不重复问）：

1. **项目名称** 和一句话描述
2. **技术栈**（语言、框架、数据库、包管理器）
3. **项目类型**（Web应用 / API服务 / CLI工具 / 库 / 全栈 / 其他）
4. **使用的 Agent 工具**（让用户从下方列表选择，默认全选）
5. **协作偏好**（读 `references/user-profile-template.md`）：整块一次性确认默认值（语言/交付标准/验证纪律/推送策略等），产出 AGENTS.md「协作约定」节 + 用户级记忆种子

如果用户已在消息中提供了足够信息，直接进入 Step 1，不追问。偏好确认也整块一次问完，不要逐条挤牙膏。

### Step 1: 执行 7 阶段搭建流程

按以下 7 个阶段依次执行。每个阶段的具体操作和文件模板见参考文件。

| 阶段 | 做什么 | 参考文件 |
|------|--------|----------|
| 0. 仓库初始化 | 生成目录结构、文档目录、初始git commit | `references/stage-0-repo-init.md` |
| 1. 环境搭建 | init脚本、feature_list.json、progress文件、浏览器自动化 | `references/stage-1-environment.md` |
| 2. 架构约束 | 分层定义、linter规则、命名规范、文件大小限制 | `references/stage-2-architecture.md` |
| 3. Agent架构 | Planner/Generator/Evaluator角色定义、Sprint合同机制 | `references/stage-3-agent-arch.md` |
| 4. 反馈循环 | 评估维度、硬阈值、失败反馈格式 | `references/stage-4-feedback.md` |
| 5. 上下文管理 | 会话启停协议、交接artifact、上下文重置规则 | `references/stage-5-context.md` |
| 6. 持续维护 | doc-gardening、质量评分、技术债务处理 | `references/stage-6-maintenance.md` |
| 7. 记忆资产 | .learnings/ 两层记忆、种子记忆、记忆纪律与衰减审查 | `references/stage-7-memory.md` |
| 8. 纪律门禁 | 修bug四步、文档≠修复、验证靠跑、commit门、多工具skill同步 | `references/stage-8-discipline.md` |

执行时机：Stage 7 紧跟 Stage 0 执行（仓库一落地就种记忆）；Stage 8 的门禁清单一次性写入 AGENTS.md，但门禁本身贯穿项目全程执行。

### Step 2: 生成 Agent 配置文件

根据用户选择的工具，生成对应配置文件。每个工具的文件格式、放置路径和内容规范见下方参考文件。

**通用标准文件（始终生成）：**

| 文件 | 路径 | 说明 | 参考文件 |
|------|------|------|----------|
| AGENTS.md | 仓库根目录 | 跨工具通用标准，60k+项目使用 | `references/config-agents-md.md` |

**工具专属文件（按用户选择生成）：**

| 工具 | 文件路径 | 参考文件 |
|------|----------|----------|
| Claude Code | `CLAUDE.md` | `references/config-claude.md` |
| GitHub Copilot | `.github/copilot-instructions.md` | `references/config-copilot.md` |
| Cursor | `.cursor/rules/*.mdc` | `references/config-cursor.md` |
| Windsurf | `.windsurfrules` | `references/config-windsurf.md` |
| Cline | `.clinerules/*.md` | `references/config-cline.md` |
| Aider | `CONVENTIONS.md` | `references/config-aider.md` |
| OpenAI Codex | `CODEX.md` | `references/config-codex.md` |
| Gemini CLI | `GEMINI.md` | `references/config-gemini.md` |

### Step 3: 验证与交付

1. 列出所有生成的文件清单
2. 提示用户检查并确认
3. 如果有 git 仓库，提示用户做初始 commit
4. 记忆检查：`.learnings/` 存在且含表头模板；工具记忆种子（用户画像/协作反馈/项目方向）已写入
5. 门禁检查：AGENTS.md 含「协作约定」与「工程纪律」节；若创建了 skill 主副本，`scripts/sync-agent-skills.sh` 已生成并执行

## 重要原则

- **AGENTS.md 是目录而非百科全书**：控制在 ~100 行，指向 docs/ 下的深层知识
- **配置文件不重复内容**：各工具文件引用 AGENTS.md 作为单一信源，只添加工具特有配置
- **JSON > Markdown**：feature_list.json 用 JSON 格式，避免模型不当修改
- **上下文重置 > 压缩**：每次会话完全清除上下文 + 结构化交接
- **一次一个特性**：每次 Agent 会话只做一个 feature
- **零手写代码原则**：让 Agent 生成脚手架，工程师设计环境和反馈循环
- **两层记忆**：仓库内 `.learnings/` 是唯一跨工具可靠沉淀；工具自带记忆只放便利信息
- **门禁要有事故实证**：写进项目的每条纪律都要能回答"没有它会出什么事故"，答不出的删掉
- **harness 假设会衰减**：模型升级后定期重审护栏清单（Anthropic Managed Agents, 2026-04-08）

## 信源

- OpenAI: Harness engineering: leveraging Codex in an agent-first world (2026-02-11)
- Anthropic: Effective harnesses for long-running agents (2025-11-26)
- Anthropic: Harness design for long-running application development (2026-03-24)
- Anthropic: Scaling Managed Agents (2026-04-08)：harness 假设衰减与稳定接口
- Mitchell Hashimoto: My AI Adoption Journey (2026-02-05)：Harness Engineering 术语源起
- Martin Fowler / Thoughtworks Technology Radar (2026-04-02)：Feedforward/Feedback 框架
- 真实项目实证：某 A 股研究项目 2026-08-29 两轮对抗审查（69 条发现）+ 259 条提交考古（纪律门禁与记忆铁律的来源）
- agents.md 标准: https://agents.md/ (Linux Foundation / AAIF)
- Claude Code 文档: https://code.claude.com/docs/
- Cline Rules 文档: https://docs.cline.bot/features/cline-rules
