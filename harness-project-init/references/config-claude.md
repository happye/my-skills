# CLAUDE.md 配置规范

## 信源
- Claude Code 文档: https://code.claude.com/docs/en/
- Claude Code 自定义为 "agentic harness"

## 文件位置
```
仓库根目录/CLAUDE.md
```

## 加载机制
- 每次会话自动加载
- 按层级加载：根目录 CLAUDE.md + 子目录 CLAUDE.md（如存在）
- 也支持 `~/.claude/CLAUDE.md`（全局用户级）

## 模板

```markdown
# CLAUDE.md — [项目名称]

> 本文件是 Claude Code 的项目配置。通用指令见 AGENTS.md。

## 引用
本文件补充 AGENTS.md，不重复其内容。完整规范见 ./AGENTS.md

## Claude Code 特有配置

### 工作流
- 新功能开发前先进入 plan mode (Shift+Tab)
- 大任务拆分为子任务，每次只做一个
- 使用 git checkpoint 在重大变更前创建检查点

### 上下文管理
- 优先使用 subagent 处理独立子任务
- 上下文接近限制时，启动新会话而非压缩
- 会话开始时读 progress.md 和 git log

### 工具偏好
- 文件搜索: 使用 grep/glob 而非逐文件读取
- 浏览器测试: 使用 Playwright MCP
- 代码搜索: 安装 code intelligence 插件用于大型代码库

### 渐进式扩展触发规则
- 两次搞错同一规范 → 加入本文件
- 反复输入同一 prompt → 存为 Skill
- 三次粘贴同一流程 → 封装为 Skill
- 数据不可见 → 连接 MCP server
- 侧任务淹没输出 → 通过 Subagent 处理
- 每次自动发生 → 写 Hook

### 禁止事项
- 不要一次性实现整个应用
- 不要跳过测试
- 不要在未运行 init.sh 的情况下开始工作
```

## 与 AGENTS.md 的关系

CLAUDE.md 只包含 Claude Code 特有的配置：
- 工作流偏好（plan mode、checkpoint）
- 工具偏好（subagent、MCP）
- 渐进式扩展规则
- 禁止事项

通用规范（架构、编码、测试）在 AGENTS.md 中，CLAUDE.md 引用而非重复。
