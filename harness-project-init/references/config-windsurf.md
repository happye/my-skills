# Windsurf 配置规范

## 信源
- Windsurf 官方文档: https://docs.windsurf.com
- 前身为 Codeium，后被 Cognition (Devin) 收购

## 文件位置

| 路径 | 作用域 |
|------|--------|
| `~/.codeium/windsurf/memories/global_rules.md` | 全局规则 |
| `仓库根目录/.windsurfrules` | 工作区规则 |

## 限制
- 每个规则文件最多 6000 字符
- 全局规则和本地规则总数不限

## 配置方式

### 方式 1: 直接放置文件
将 `.windsurfrules` 文件放在项目根目录。

### 方式 2: 通过设置界面
Windsurf Settings > Set Workspace AI Rules > Edit Rules

## 模板

### .windsurfrules

```markdown
# Windsurf Rules — [项目名称]

> 通用 Agent 指令见 ./AGENTS.md，本文件仅包含 Windsurf 特有配置。

## 技术栈
- [技术栈详情]

## Cascade 行为规则
- 使用 Agent 模式处理复杂任务
- 使用 Copilot 模式进行实时协助
- 大任务拆分为小步骤，逐步确认

## 代码生成偏好
- TypeScript strict mode
- 优先使用函数组合而非继承
- 错误处理使用 Result 类型模式

## 禁止事项
- 不要生成 mock 数据代替真实 API 调用
- 不要跳过类型检查
- 不要在单个文件中实现多个功能模块
```

## 与 AGENTS.md 的关系

Windsurf 通过 AGENTS.md 标准兼容。
`.windsurfrules` 补充 Windsurf Cascade 特有的行为规则。
注意 6000 字符限制，保持简洁。
