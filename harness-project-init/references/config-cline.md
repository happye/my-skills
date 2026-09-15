# Cline 配置规范

## 信源
- Cline 官方文档: https://docs.cline.bot/features/cline-rules
- Cline 是 VS Code 扩展，支持多种规则格式

## 文件位置

| 路径 | 作用域 | 说明 |
|------|--------|------|
| `.clinerules/*.md` | 工作区 | Cline 原生格式 |
| `.cursorrules` | 工作区 | 自动检测 Cursor 格式 |
| `.windsurfrules` | 工作区 | 自动检测 Windsurf 格式 |
| `AGENTS.md` | 工作区 | 自动检测通用格式 |
| `~/.agents/AGENTS.md` | 全局 | 跨工具全局指令 |
| `Documents\Cline\Rules\` (Windows) | 全局 | Cline 全局规则目录 |

## 规则文件格式

纯 Markdown 文件，每个文件聚焦一个关注点：

```
.clinerules/
├── coding.md          # 编码标准
├── testing.md         # 测试要求
├── architecture.md    # 架构决策
└── security.md        # 安全规则
```

Cline 处理所有 `.md` 和 `.txt` 文件，合并为统一规则集。
数字前缀（如 `01-coding.md`）帮助排序但可选。

## 规则开关

每个规则文件可在 Rules 面板中单独启用/禁用，无需删除文件。

## 模板

### .clinerules/coding.md

```markdown
# 编码标准

> 完整规范见 ./AGENTS.md

## 代码风格
- TypeScript strict mode
- 单引号，无分号
- 优先使用函数式模式

## 文件组织
- 一个组件一个文件
- 文件名 kebab-case
- 单文件不超过 300 行

## 错误处理
- 所有 async 函数使用 try-catch
- 错误信息对用户友好
- 不暴露技术细节给前端
```

### .clinerules/testing.md

```markdown
# 测试要求

## 单元测试
- 业务逻辑必须有单元测试
- 测试文件命名: [filename].test.ts
- 使用 describe/it 组织测试

## 集成测试
- API 端点必须有集成测试
- 测试所有成功和失败路径

## E2E 测试
- 关键用户流程必须有 E2E 测试
- 使用 Playwright
```

## 与 AGENTS.md 的关系

Cline 自动检测 AGENTS.md 并加载。
`.clinerules/` 补充 Cline 特有的文件级规则拆分和开关机制。
工作区规则优先于全局规则。

## 条件规则

Cline 支持条件规则，仅在编辑匹配文件时激活：

```markdown
---
globs: ["src/frontend/**"]
---

# 前端规则（仅编辑前端文件时激活）

- 使用 React Server Components
- 样式使用 Tailwind CSS
```
