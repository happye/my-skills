# Harness Project Init

> 基于官方信源 + 真实项目实证的新项目 Harness Engineering 一键搭建 Skill。
> 说"新建项目"，自动生成 9 阶段工程脚手架（含记忆资产与纪律门禁）+ 9 种主流 Agent 工具配置文件。

## 这是什么

一个 QClaw Skill。当你说"新建项目""搭建脚手架""harness"时自动触发，帮你：

1. 生成标准目录结构和文档体系
2. 搭建让 Agent 能自主开发的环境（init 脚本、特性列表、进度追踪）
3. 定义架构约束（分层、linter、命名规范）
4. 建立 Planner → Generator → Evaluator 三 Agent 协作架构
5. 配置反馈循环（4 维度评分，硬阈值 ≥ 7）
6. 设置上下文管理协议（重置 > 压缩，结构化交接）
7. 生成持续维护机制（doc-gardening、技术债务处理）
8. 搭建两层记忆资产（.learnings/ 跨工具沉淀 + 工具记忆种子 + 衰减审查）
9. 落地工程纪律门禁（修bug四步、文档≠修复、验证靠跑、commit 门、多工具 skill 同步）
10. 收集并固化你的协作偏好（语言/交付/验证/推送策略 → AGENTS.md + 用户记忆）
11. 为你使用的每个 Agent 工具生成对应配置文件

## 触发方式

在 QClaw 对话中说以下任意关键词：

```
新建项目 / 初始化项目 / 搭建脚手架 / harness / 新仓库 /
project setup / scaffold / 开始新项目
```

## 执行流程

```
用户说"新建项目"
    │
    ▼
Step 0: 收集信息（项目名、技术栈、类型、Agent 工具、协作偏好确认）
    │
    ▼
Step 1: 阶段化搭建（Stage 0-8）
    ├─ Stage 0: 仓库初始化（目录 + AGENTS.md + docs/ + git）
    ├─ Stage 1: 环境搭建（init.sh + feature_list.json + progress.md + Playwright）
    ├─ Stage 2: 架构约束（分层 + linter + 不变量）
    ├─ Stage 3: Agent 架构（Planner / Generator / Evaluator + Sprint 合同）
    ├─ Stage 4: 反馈循环（4 维度评分 + 硬阈值 ≥ 7 + 闭环修复）
    ├─ Stage 5: 上下文管理（会话启停协议 + 3 个交接文件 + 重置 > 压缩）
    ├─ Stage 6: 持续维护（doc-gardening + 质量扫描 + 技术债务）
    ├─ Stage 7: 记忆资产（.learnings/ 两层记忆 + 种子 + 衰减审查）
    └─ Stage 8: 纪律门禁（修bug四步 + commit 门 + 多工具 skill 同步）
    │
    ▼
Step 2: 生成 Agent 配置文件
    ├─ AGENTS.md（始终生成，通用标准）
    ├─ CLAUDE.md（Claude Code）
    ├─ .github/copilot-instructions.md（GitHub Copilot）
    ├─ .cursor/rules/*.mdc（Cursor）
    ├─ .windsurfrules（Windsurf）
    ├─ .clinerules/*.md（Cline）
    ├─ CONVENTIONS.md（Aider）
    ├─ CODEX.md（OpenAI Codex）
    └─ GEMINI.md（Gemini CLI）
    │
    ▼
Step 3: 验证与交付（文件清单 → 用户确认 → git commit）
```

## 覆盖的 Agent 工具

| 工具 | 配置文件 | 路径 | 特点 |
|------|----------|------|------|
| 通用标准 | AGENTS.md | 仓库根目录 | 60k+ 项目使用，Linux Foundation 维护，兼容 20+ 工具 |
| Claude Code | CLAUDE.md | 仓库根目录 | plan mode、subagent、渐进式扩展 |
| GitHub Copilot | copilot-instructions.md | .github/ | 支持路径级模块化指令 |
| Cursor | *.mdc | .cursor/rules/ | 4 种规则类型（Always/Auto/Agent/Manual） |
| Windsurf | .windsurfrules | 仓库根目录 | 6000 字符限制 |
| Cline | *.md | .clinerules/ | 自动检测其他工具格式，规则可开关 |
| Aider | CONVENTIONS.md | 仓库根目录 | 终端 pair programming |
| OpenAI Codex | CODEX.md | 仓库根目录 | 零手写代码原则 |
| Gemini CLI | GEMINI.md | 仓库根目录 | 多模态分析 |

## 核心原则

| 原则 | 说明 |
|------|------|
| AGENTS.md 是目录不是百科 | ~100 行，指向 docs/ 下深层知识 |
| 配置不重复 | 各工具文件引用 AGENTS.md，只加工具特有配置 |
| JSON > Markdown | feature_list.json 用 JSON，防模型乱改结构 |
| 上下文重置 > 压缩 | 完全清除 + 结构化交接，优于同一 Agent 压缩 |
| 一次一个特性 | 每次 Agent 会话只做一个 feature |
| 零手写代码 | Agent 生成脚手架，工程师设计环境和反馈循环 |
| 两层记忆 | .learnings/ 是唯一跨工具可靠沉淀；工具记忆只放便利信息 |
| 门禁要有实证 | 每条纪律都能回答"没有它会出什么事故"，答不出的删掉 |
| harness 会衰减 | 模型升级后定期重审护栏（Anthropic Managed Agents, 2026-04-08） |

## 信源

全部来自官方，无第三方博客：

| 来源 | 日期 | 贡献 |
|------|------|------|
| OpenAI 工程博客 | 2026-02-11 | Harness Engineering 概念提出 |
| Anthropic 工程博客 | 2025-11-26 | initializer + coding agent + progress 机制 |
| Anthropic 工程博客 | 2026-03-24 | Planner/Generator/Evaluator 三 Agent 体系 |
| Anthropic 工程博客 | 2026-04-08 | Managed Agents：harness 假设衰减、稳定接口 |
| Mitchell Hashimoto | 2026-02-05 | Harness Engineering 术语源起 |
| Martin Fowler / Thoughtworks | 2026-04-02 | Feedforward/Feedback 框架 |
| 真实项目对抗审查 | 2026-08-29 | 69 条发现 + 259 条提交考古 → 纪律门禁与记忆铁律 |
| agents.md | 持续维护 | 跨工具通用标准（Linux Foundation / AAIF） |
| Cline 官方文档 | 持续维护 | .clinerules 规则格式 |
| Claude Code 文档 | 持续维护 | CLAUDE.md 配置规范 |
| GitHub Copilot 文档 | 持续维护 | copilot-instructions.md 配置 |

## 文件结构

```
harness-project-init/
├── SKILL.md                          # 主文件：触发条件 + 执行流程 + 索引
└── references/                       # 19 个参考文件
    ├── stage-0-repo-init.md          # 仓库初始化模板
    ├── stage-1-environment.md        # 环境搭建模板
    ├── stage-2-architecture.md       # 架构约束模板
    ├── stage-3-agent-arch.md         # Agent 架构设计
    ├── stage-4-feedback.md           # 反馈循环机制
    ├── stage-5-context.md            # 上下文管理协议
    ├── stage-6-maintenance.md        # 持续维护机制
    ├── stage-7-memory.md             # 记忆资产模板（两层记忆 + 衰减审查）
    ├── stage-8-discipline.md         # 工程纪律门禁（通用化，事故实证）
    ├── user-profile-template.md      # 用户协作偏好收集与记忆种子模板
    ├── config-agents-md.md           # AGENTS.md 配置规范
    ├── config-claude.md              # Claude Code 配置规范
    ├── config-copilot.md             # GitHub Copilot 配置规范
    ├── config-cursor.md              # Cursor 配置规范
    ├── config-windsurf.md            # Windsurf 配置规范
    ├── config-cline.md               # Cline 配置规范
    ├── config-aider.md               # Aider 配置规范
    ├── config-codex.md               # OpenAI Codex 配置规范
    └── config-gemini.md              # Gemini CLI 配置规范
```

## 使用示例

```
你: 新建一个项目，React + Node.js 全栈，用 Claude Code 和 Cursor

AI: （自动触发 skill）
    1. 确认信息：React+Node.js 全栈，工具选 Claude Code + Cursor
    2. 执行 7 阶段搭建...
    3. 生成文件清单：
       - AGENTS.md（通用）
       - CLAUDE.md（Claude Code）
       - .cursor/rules/general.mdc（Cursor）
       - .cursor/rules/frontend.mdc（Cursor，前端规则）
       - scripts/init.sh
       - feature_list.json
       - progress.md
       - docs/design-docs/
       - docs/exec-plans/
       - docs/product-specs/
       - docs/references/
    4. 请检查并确认，确认后做 git init + 首次 commit
```

## 安装

本 Skill 位于用户级 skill 目录，各工具自动加载。已同步三份：`~/.claude/skills/harness-project-init/`（Claude Code）、`~/.qclaw/skills/harness-project-init/`（QClaw）、`~/.codex/skills/harness-project-init/`（Codex）。更新任何一份后，把整个目录复制到其余两份保持一致（正是本 skill 门禁 7 教的做法）。

## 版本

- v1.0 — 2026-07-22 — 初始版本
- v2.0 — 2026-09-15 — 新增记忆资产（Stage 7）、工程纪律门禁（Stage 8）、用户协作偏好收集；吸收 Anthropic Managed Agents「harness 假设衰减」与 Martin Fowler Feedforward/Feedback 框架
