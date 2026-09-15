# Aider 配置规范

## 信源
- Aider 官方文档: https://aider.chat/docs/usage/conventions.html
- Aider 是终端中的 AI pair programming 工具

## 文件位置

| 路径 | 作用域 | 说明 |
|------|--------|------|
| `CONVENTIONS.md` | 仓库级 | Aider 约定文件，自动加载 |
| `.aider.conf.yml` | 仓库级 | Aider 配置文件 |
| `~/.aider.conf.yml` | 全局 | 全局 Aider 配置 |

## CONVENTIONS.md

Aider 会在每次会话中自动加载 `CONVENTIONS.md`。

## 模板

### CONVENTIONS.md

```markdown
# Coding Conventions — [项目名称]

> 通用 Agent 指令见 ./AGENTS.md，本文件包含 Aider 特有约定。

## 代码风格
- TypeScript strict mode
- 单引号，无分号
- 优先使用函数式模式
- 文件名 kebab-case

## 提交规范
- 使用 conventional commits
- 提交前运行 lint 和 test
- 不要提交 console.log / debug 语句

## 编辑规则
- 修改代码前先阅读相关文件
- 保持现有代码风格
- 不要做无关的重构
- 每次只修改一个功能点
```

### .aider.conf.yml

```yaml
# Aider 配置
model: claude-sonnet-4-20250514
auto-commits: true
auto-lint: true
lint-cmd: npm run lint
test-cmd: npm test
edit-format: diff
```

## 与 AGENTS.md 的关系

Aider 也支持读取 AGENTS.md。
`CONVENTIONS.md` 补充 Aider 特有的 pair programming 约定。
