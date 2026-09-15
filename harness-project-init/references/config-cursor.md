# Cursor 配置规范

## 信源
- Cursor 官方文档: https://docs.cursor.com
- Cursor Rules: https://cursor.com/docs/rules

## 文件位置

### 旧格式（已弃用但仍支持）
```
仓库根目录/.cursorrules    # 单文件，纯文本/Markdown
```

### 新格式（推荐）
```
仓库根目录/.cursor/rules/*.mdc    # 模块化规则文件
```

## 规则类型（.mdc 文件）

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| Always | 始终应用 | 全局规范 |
| Auto Attached | 匹配 globs 时自动附加 | 特定文件类型规则 |
| Agent Requested | Agent 自行判断是否应用 | 可选参考资料 |
| Manual | 仅 @规则名 时附加 | 特定任务规则 |

## .mdc 文件格式

```yaml
---
description: 前端开发规则
globs: ["src/frontend/**", "*.tsx", "*.jsx"]
alwaysApply: false
---

# 前端开发规则

- 使用 React Server Components 优先
- 客户端组件标注 "use client"
- 样式使用 Tailwind CSS
- 组件命名: PascalCase
- 一个组件一个文件
```

## 推荐文件结构

```
.cursor/
└── rules/
    ├── general.mdc           # Always - 通用规范
    ├── frontend.mdc          # Auto Attached - 前端规则
    ├── backend.mdc           # Auto Attached - 后端规则
    ├── database.mdc          # Auto Attached - 数据库规则
    ├── testing.mdc           # Always - 测试规范
    └── deployment.mdc        # Manual - 部署规则
```

## 模板

### .cursor/rules/general.mdc

```yaml
---
description: 项目通用规范
globs: []
alwaysApply: true
---

# 项目通用规范

> 完整 Agent 指令见 ./AGENTS.md

## 技术栈
- [技术栈详情]

## 代码风格
- [代码风格规则]

## 禁止事项
- 不要使用 any 类型
- 不要跳过 TypeScript 检查
- 不要在组件中直接调用数据库
```

## 与 AGENTS.md 的关系

Cursor 也支持读取 AGENTS.md。
`.cursor/rules/` 文件补充 Cursor 特有的规则类型和 globs 匹配机制。
通用规范在 AGENTS.md 中，Cursor rules 引用而非重复。
