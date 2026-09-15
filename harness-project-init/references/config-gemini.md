# Gemini CLI 配置规范

## 信源
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Jules (Google): https://jules.google
- Gemini CLI 是 Google 的终端 AI 编程工具

## 文件位置

| 路径 | 作用域 | 说明 |
|------|--------|------|
| `GEMINI.md` | 仓库级 | Gemini CLI 项目配置 |
| `AGENTS.md` | 仓库级 | Gemini 也支持 AGENTS.md 标准 |
| `~/.gemini/settings.json` | 全局 | 全局 Gemini CLI 设置 |

## 模板

### GEMINI.md

```markdown
# Gemini CLI Configuration — [项目名称]

> 通用 Agent 指令见 ./AGENTS.md，本文件包含 Gemini CLI 特有配置。

## 项目上下文
- 技术栈: [技术栈]
- 框架: [框架名 + 版本]
- 包管理器: [包管理器]

## Gemini CLI 工作流
- 使用 plan 模式先规划再执行
- 大任务拆分为小步骤
- 使用 Gemini 的多模态能力分析截图

## 代码生成偏好
- [语言] strict mode
- 优先使用 [编码风格]
- 错误处理: [错误处理规范]

## 禁止事项
- 不要跳过类型检查
- 不要在未运行测试的情况下提交
- 不要一次性修改多个不相关的模块
```

### ~/.gemini/settings.json

```json
{
  "model": "gemini-2.5-pro",
  "temperature": 0.1,
  "max_tokens": 8192
}
```

## 与 AGENTS.md 的关系

Gemini CLI 支持 AGENTS.md 标准。
`GEMINI.md` 补充 Gemini 特有的配置，如多模态分析偏好。
通用规范在 AGENTS.md 中。

## Jules (Google) 兼容性

Google Jules 也支持 AGENTS.md 标准。
如果同时使用 Gemini CLI 和 Jules，AGENTS.md 作为共用配置即可。
