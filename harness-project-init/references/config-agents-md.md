# AGENTS.md 配置规范

## 信源
- 官方网站: https://agents.md/
- 标准维护: Agentic AI Foundation (AAIF) under Linux Foundation
- 采用项目: 60,000+ 开源项目

## 文件位置
```
仓库根目录/AGENTS.md
```

## 兼容工具（官方列表）
Codex (OpenAI)、Jules (Google)、Factory、Aider、Goose、OpenCode、Zed、Warp、VS Code、Devin (Cognition)、UiPath、Junie (JetBrains)、Amp、Cursor、RooCode、Gemini CLI (Google)、Kilo Code、Phoenix、Semgrep、GitHub Copilot Coding Agent、Ona、Windsurf (Cognition)、Augment Code

## 与其他配置文件的关系

AGENTS.md 是**通用标准**，其他工具配置文件引用它而非重复内容：

```
AGENTS.md          ← 单一信源（~100行目录）
├── CLAUDE.md      ← 引用 AGENTS.md + Claude 特有配置
├── .github/copilot-instructions.md ← 引用 AGENTS.md + Copilot 特有配置
├── .cursor/rules/ ← 引用 AGENTS.md + Cursor 特有配置
└── ...
```

## 模板

```markdown
# AGENTS.md — [项目名称]

> 本文件是 Agent 的导航目录。详细文档在 docs/ 下。
> 兼容 agents.md 标准 (https://agents.md/)

## 项目概述
[一句话描述]

## 开发环境
- 包管理器: [pnpm/npm/pip/cargo/go]
- 安装依赖: `[安装命令]`
- 启动开发服务器: `./scripts/init.sh`
- 运行测试: `[测试命令]`
- 构建生产版本: `[构建命令]`

## 架构分层
Types → Config → Repo → Service → Runtime → UI
详见 docs/design-docs/architecture.md

## 编码规范
- [语言] strict mode
- 命名: 文件 kebab-case, 类 PascalCase, 变量 camelCase
- 单文件不超过 300 行
- 函数圈复杂度不超过 10
- 详见 docs/references/coding-standards.md

## 测试要求
- 单元测试覆盖业务逻辑
- 集成测试覆盖 API 端点
- E2E 测试覆盖关键用户流程
- 提交前必须通过所有测试
- 详见 docs/references/testing-guide.md

## PR 规范
- 标题格式: `[类型]([特性ID]): [描述]`
- 提交前运行 `[lint命令]` 和 `[测试命令]`
- PR 描述包含: 变更内容、测试方式、影响范围

## 安全注意事项
- 永远不要在代码中硬编码密钥
- 用户输入必须经过校验
- SQL 查询必须使用参数化

## 文档索引
- 产品规格: docs/product-specs/
- 设计文档: docs/design-docs/
- 执行计划: docs/exec-plans/
- 参考资料: docs/references/
```

## 大型 monorepo

在子目录放置嵌套 AGENTS.md，Agent 自动读取最近的文件：

```
monorepo/
├── AGENTS.md              # 全局指令
├── packages/
│   ├── frontend/
│   │   └── AGENTS.md      # 前端特有指令
│   ├── backend/
│   │   └── AGENTS.md      # 后端特有指令
│   └── shared/
│       └── AGENTS.md      # 共享库特有指令
```
