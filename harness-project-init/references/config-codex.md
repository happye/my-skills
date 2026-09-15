# OpenAI Codex 配置规范

## 信源
- OpenAI Codex: https://openai.com/codex/
- Codex 是 OpenAI 的 CLI AI 编程智能体
- AGENTS.md 标准由 OpenAI Codex 团队参与创建

## 文件位置

| 路径 | 作用域 | 说明 |
|------|--------|------|
| `AGENTS.md` | 仓库级 | Codex 原生支持，主要配置文件 |
| `CODEX.md` | 仓库级 | Codex 专属补充配置 |
| `~/.codex/config.json` | 全局 | 全局 Codex 配置 |

## 与 AGENTS.md 的关系

Codex 是 AGENTS.md 标准的发起者之一，原生支持 AGENTS.md。
`CODEX.md` 是可选的 Codex 专属补充文件。

## 模板

### CODEX.md

```markdown
# Codex Configuration — [项目名称]

> 完整 Agent 指令见 ./AGENTS.md，本文件包含 Codex 特有配置。

## Codex 工作模式
- 零手写代码原则: 所有代码由 Codex 生成
- 工程师角色: 设计环境、描述意图、构建反馈循环
- Codex 开 PR，Agent 之间互相 review

## 自主等级
- 可自主: 验证代码库 → 复现 bug → 实现 → 测试 → 开 PR
- 需人工判断: 架构决策、产品方向、安全敏感操作

## 应用可读性要求
- 每个应用实例可通过 init.sh 启动
- 日志输出为结构化格式
- 健康检查端点: /health
- 指标端点: /metrics

## 仓库知识管理
- AGENTS.md 是目录（~100行），指向 docs/ 下深层知识
- 不写巨大的 AGENTS.md
- 所有决策沉淀到仓库（Agent 看不到的等于不存在）
- 偏好"无聊"的技术（更稳定、更可组合）
```

## 关键原则（来自 OpenAI Harness Engineering 原始博客）

- **零手写代码**：让 Codex 生成所有代码
- **应用可读性**：让 Codex 能读取 UI、日志、指标
- **仓库知识 = 系统记录**：AGENTS.md 是目录
- **强制架构和品味**：通过 linter 而非微管理
- **吞吐量 > 阻塞**：在高吞吐环境中，纠正成本低，等待成本高
- **熵与垃圾回收**：定期扫描偏差，持续偿还技术债务
