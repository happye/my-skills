# Stage 0: 仓库初始化

## 目标
用 Agent 生成初始仓库结构，建立文档体系，初始 git commit。

## 操作清单

### 0.1 生成目录结构

根据项目类型生成标准目录：

```
project-root/
├── src/                    # 源代码
├── tests/                  # 测试文件
├── docs/                   # 结构化文档目录
│   ├── design-docs/        # 设计文档
│   ├── exec-plans/         # 执行计划
│   ├── product-specs/      # 产品规格
│   └── references/         # 参考资料
├── scripts/                # 工具脚本
├── .github/                # CI/CD 配置
│   └── workflows/
├── AGENTS.md               # 跨工具通用 Agent 指令（~100行目录）
├── CLAUDE.md               # Claude Code 配置（如选择）
├── .cursor/rules/          # Cursor 规则（如选择）
├── .windsurfrules          # Windsurf 规则（如选择）
├── .clinerules/            # Cline 规则（如选择）
├── CONVENTIONS.md          # Aider 约定（如选择）
├── CODEX.md                # Codex 配置（如选择）
├── GEMINI.md               # Gemini CLI 配置（如选择）
├── .github/copilot-instructions.md  # Copilot 指令（如选择）
└── feature_list.json       # 特性列表（JSON 格式）
```

### 0.2 生成 AGENTS.md

AGENTS.md 是**目录而非百科**，控制在 ~100 行：

```markdown
# AGENTS.md — [项目名称]

> 本文件是 Agent 的导航目录。详细文档在 docs/ 下。

## 项目概述
[一句话描述]

## 开发环境
- 包管理器: [pnpm/npm/pip/cargo/go]
- 启动命令: `./scripts/init.sh`
- 测试命令: `[命令]`
- 构建命令: `[命令]`

## 架构分层
Types → Config → Repo → Service → Runtime → UI
详见 docs/design-docs/architecture.md

## 编码规范
详见 docs/references/coding-standards.md

## 测试要求
详见 docs/references/testing-guide.md

## 文档索引
- 产品规格: docs/product-specs/
- 设计文档: docs/design-docs/
- 执行计划: docs/exec-plans/
- 参考资料: docs/references/
```

### 0.3 建立文档目录

创建 `docs/` 下的四个子目录，每个目录放置一个 `.gitkeep` 或占位 README：

- `docs/design-docs/` — 架构决策记录 (ADR)、技术设计
- `docs/exec-plans/` — Sprint 计划、执行方案
- `docs/product-specs/` — 产品需求文档、特性列表
- `docs/references/` — API 文档、编码规范、测试指南

### 0.4 初始 git commit

```bash
git init
git add -A
git commit -m "chore: initialize project with harness engineering scaffold"
```

## 关键原则

- **零手写代码**：让 Agent 生成所有脚手架代码
- **AGENTS.md 是目录**：~100 行，指向 docs/ 下的深层知识，不要写成百科全书
- **不写巨大的 AGENTS.md**：会导致上下文污染、规则腐烂、难以验证
- **结构化文档**：所有决策、计划、规范沉淀到仓库中（Agent 看不到的东西等于不存在）
