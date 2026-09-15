# GitHub Copilot 配置规范

## 信源
- GitHub Copilot 文档: https://docs.github.com/copilot
- copilot-instructions.md 是 Copilot Chat 的指令文件

## 文件位置（按优先级）

| 路径 | 作用域 |
|------|--------|
| `~/.copilot/copilot-instructions.md` | 全局（所有会话） |
| `.github/copilot-instructions.md` | 仓库级 |
| `.github/instructions/**/*.instructions.md` | 模块化（路径级） |

仓库级指令始终优先于全局指令。

## 启用方式
在 VS Code 中设置 `github.copilot.chat.codeGeneration.useInstructionFiles` 为 `true`。

## 模板

### .github/copilot-instructions.md

```markdown
# Copilot Instructions — [项目名称]

> 通用 Agent 指令见 ./AGENTS.md，本文件仅包含 Copilot 特有配置。

## 项目上下文
- 技术栈: [技术栈]
- 框架: [框架名 + 版本]
- 包管理器: [包管理器]

## 代码生成规则
- 使用 TypeScript strict mode
- 优先使用函数式模式
- 错误处理: 所有 async 函数使用 try-catch
- 导入: 使用相对路径，不使用别名

## 路径级指令引用
- 前端规则: .github/instructions/frontend.instructions.md
- 后端规则: .github/instructions/backend.instructions.md
- 数据库规则: .github/instructions/database.instructions.md
```

### .github/instructions/frontend.instructions.md

```markdown
---
applyTo: "src/frontend/**"
---

# 前端开发规则

- 使用 React Server Components 优先
- 客户端组件标注 "use client"
- 样式使用 Tailwind CSS
- 组件命名: PascalCase
- 一个组件一个文件
```

## 与 AGENTS.md 的关系

Copilot 也支持读取 AGENTS.md（在 Git 根目录或当前工作目录）。
`.github/copilot-instructions.md` 补充 Copilot Chat 特有的代码生成规则。
