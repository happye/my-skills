# Stage 1: 环境搭建

## 目标
让 Agent 能独立启动应用、运行测试、获取反馈。

## 操作清单

### 1.1 编写 init.sh 脚本

在 `scripts/init.sh` 中编写开发环境启动脚本：

```bash
#!/usr/bin/env bash
set -euo pipefail

# 安装依赖
[包管理器] install

# 启动开发服务器（后台）
[启动命令] &

# 等待服务器就绪
while ! curl -s http://localhost:[端口]/health > /dev/null 2>&1; do
  sleep 1
done

echo "Development server is ready at http://localhost:[端口]"
```

Windows 对应 `scripts/init.ps1`。

### 1.2 创建 feature_list.json

**用 JSON 而非 Markdown**，因为模型不太会不当修改 JSON。

```json
{
  "project": "[项目名称]",
  "version": "0.1.0",
  "features": [
    {
      "id": "F001",
      "name": "用户注册",
      "description": "用户可通过邮箱注册账号",
      "priority": 1,
      "passes": false,
      "test_criteria": "注册成功后数据库中有对应用户记录，返回201状态码"
    },
    {
      "id": "F002",
      "name": "用户登录",
      "description": "已注册用户可登录获取token",
      "priority": 2,
      "passes": false,
      "test_criteria": "正确凭据返回200和JWT token，错误凭据返回401"
    }
  ]
}
```

将用户需求扩展为 200+ 个具体特性描述，每个标记 `passes: false`。

### 1.3 创建 progress 文件

`progress.md`（或 `.txt`）— 记录 Agent 已完成的工作日志：

```markdown
# Progress Log

## [日期] - Session Start
- Current feature: [F001 - 用户注册]
- Status: in progress
- Notes: [记录]

## [日期] - Session End
- Completed: [F001 - 用户注册]
- Commit: [hash]
- Next: [F002 - 用户登录]
```

### 1.4 接入浏览器自动化

提供 Playwright/Puppeteer MCP 配置，让 Agent 像人类用户一样测试：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/mcp-playwright"]
    }
  }
}
```

### 1.5 暴露日志/指标给 Agent

- 确保应用日志输出到文件（Agent 可读）
- 暴露健康检查端点 `/health`
- 暴露指标端点 `/metrics`（如适用）

## 关键原则

- **init.sh 是 Agent 的启动按钮**：每次会话开始第一步就是运行它
- **feature_list.json 用 JSON**：防止模型不当修改结构化数据
- **progress 文件是交接 artifact**：让新 Agent 快速了解项目状态
- **浏览器自动化 = 端到端验证**：让 Agent 像用户一样点击测试
