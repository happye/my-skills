# Stage 2: 架构约束

## 目标
通过不变量（invariants）而非微管理来保持一致性。让 Agent 在约束内自由发挥。

## 操作清单

### 2.1 定义分层架构

每个业务域按以下层次组织：

```
Types    → 类型定义（无依赖）
Config   → 配置（依赖 Types）
Repo     → 数据访问（依赖 Types + Config）
Service  → 业务逻辑（依赖 Repo）
Runtime  → 运行时编排（依赖 Service）
UI       → 用户界面（依赖 Runtime）
```

在 `docs/design-docs/architecture.md` 中记录分层规则。

### 2.2 编写自定义 linter 规则

用 linter 强制依赖方向，而非人工 review：

```yaml
# .eslintrc.yml 示例
rules:
  no-restricted-imports:
    - error
    - paths:
      - name: "src/ui"
        message: "UI 层不能被其他层导入"
      - name: "src/runtime"
        message: "Runtime 层只能被 UI 层导入"
```

### 2.3 定义品味不变量

在 `docs/references/coding-standards.md` 中记录：

- **结构化日志**：所有日志使用统一格式（JSON / logfmt）
- **命名规范**：文件名 kebab-case，类名 PascalCase，变量 camelCase
- **文件大小限制**：单个文件不超过 300 行
- **函数复杂度**：圈复杂度不超过 10
- **导入顺序**：标准库 → 第三方 → 内部模块

### 2.4 lint 错误信息注入修复指令

让 lint 错误信息直接告诉 Agent 怎么修：

```javascript
// eslint-plugin-custom-rules/index.js
module.exports = {
  rules: {
    "no-console": {
      meta: {
        message: "不要使用 console.log。请使用 src/utils/logger.ts 中的 logger.info() 代替。示例: logger.info('message', { context: 'value' })"
      }
    }
  }
}
```

### 2.5 设置结构测试

用 dependency-cruiser 等工具验证模块依赖关系：

```json
{
  "forbidden": [
    {
      "name": "ui-not-imported-by-others",
      "from": {},
      "to": { "path": "^src/ui/" }
    }
  ]
}
```

## 关键原则

- **不变量 > 微管理**：定义"什么不能变"而非"必须怎么做"
- **linter 是 Agent 的护栏**：自动执行，无需人工干预
- **错误信息 = 修复指令**：让 Agent 能自动修复 lint 错误
- **结构测试**：自动验证模块边界不被打破
