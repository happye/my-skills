# Stage 5: 上下文管理

## 目标
通过上下文重置 + 结构化交接，让 Agent 跨会话持续工作。

## 核心原则：上下文重置 > 压缩

完全清除上下文并启动新 Agent + 结构化交接，优于在同一 Agent 中压缩。

原因：同一 Agent 中压缩会导致"上下文焦虑"——模型担心遗漏信息，表现下降。

## 会话启动协议

每次 Agent 会话开始时执行：

```
1. pwd                    → 确认工作目录正确
2. git log --oneline -10  → 了解最近 10 次提交
3. 读 progress.md         → 了解当前工作状态
4. 读 feature_list.json   → 选择下一个要做的特性
5. 运行 ./scripts/init.sh → 启动开发服务器
6. 基本端到端测试          → 确认应用正常运行
```

## 会话结束协议

每次 Agent 会话结束时执行：

```
1. git add -A
2. git commit -m "feat([特性ID]): [描述]"
3. 更新 progress.md:
   - 本会话完成了什么
   - 当前特性状态（in_progress / completed）
   - 下一步建议
4. 如果特性完成: 更新 feature_list.json 中对应 passes: true
```

## 交接 Artifact

三个关键交接文件：

### progress.md（工作日志）

```markdown
# Progress Log

## 2026-07-18 Session 1
- Started: F001 - 用户注册
- Status: completed
- Commit: a1b2c3d
- Notes: 实现了邮箱注册，密码加密使用 bcrypt

## 2026-07-18 Session 2
- Started: F002 - 用户登录
- Status: in_progress
- Commit: e4f5g6h (WIP)
- Notes: JWT token 生成已完成，中间件待实现
- Blockers: 需要 Redis 配置用于 token 黑名单
```

### feature_list.json（特性列表）

```json
{
  "features": [
    { "id": "F001", "name": "用户注册", "passes": true, "completed_at": "2026-07-18" },
    { "id": "F002", "name": "用户登录", "passes": false, "in_progress": true }
  ]
}
```

### git log（提交历史）

描述性提交信息是交接的一部分：

```
a1b2c3d feat(F001): 实现用户注册功能
e4f5g6h wip(F002): JWT token 生成
```

## 一次一个特性

**每次会话只做一个特性**。原因：
- 避免上下文耗尽时功能半成品
- 确保每个特性得到充分关注
- 符合增量交付理念

## 关键原则

- **上下文重置 > 压缩**：新会话 + 结构化交接 > 同一会话压缩
- **三个交接文件**：progress.md + feature_list.json + git log
- **一次一个特性**：不多做，不贪多
- **描述性提交信息**：让 git log 本身成为交接文档
