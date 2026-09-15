# My Skills

Personal collection of AI Agent skills. Each skill is self-contained and dependency-free.

## Skills

| Skill | Description |
|-------|-------------|
| `dev-flow` | Universal development workflow: plan, diagnose, implement, verify, sync, ship. Self-contained, zero dependencies, works on any project. Integrates YAGNI, Rule of Three, TDD Bug Fixing, Graceful Degradation, SemVer. |
| `fin-crisis-monitor` | 金融危机地基信号监控：美债10年收益率 + 美元指数定时预警系统。多数据源容错（东方财富 push2/K线 + 新浪）、三级双向预警（🟡🟠🔴 + 共振）、QuickChart 走势图、微信推送。Python 零依赖。 |
| `harness-project-init` | 新项目初始化的 Harness Engineering 一键搭建：9 阶段脚手架（仓库/环境/架构/Agent架构/反馈/上下文/维护/**记忆资产/纪律门禁**）+ 9 种主流 Agent 工具配置（AGENTS.md/CLAUDE.md/Copilot/Cursor/Windsurf/Cline/Aider/Codex/Gemini）+ 用户协作偏好固化。官方信源 + 真实项目对抗审查实证。 |

## Installation

Copy any skill directory to your agent's skills directory.

```bash
# Codex
cp -r dev-flow ~/.codex/skills/

# Claude Code
cp -r dev-flow ~/.claude/skills/

# OpenClaw / QClaw
cp -r fin-crisis-monitor ~/.qclaw/skills/
```

Each skill works independently. No cross-skill dependencies.

## fin-crisis-monitor — 金融危机预警

监控两大"地基信号"：**美债10年收益率**和**美元指数**。每天三次定时获取数据、计算趋势变动、分级预警、生成走势图、通过微信推送。

### 快速开始

```bash
# 1. 复制脚本到 workspace
cp fin-crisis-monitor/scripts/fin_crisis_monitor.py <workspace>/scripts/

# 2. 一键部署（生成 cron 任务配置）
python fin-crisis-monitor/scripts/deploy.py --workspace <workspace> --wechat-id <你的微信ID>
```

### 特性

- **多数据源容错**：东方财富 push2 → 东方财富 K线 → 新浪财经，逐个降级
- **反爬策略**：UA 轮换、随机延迟、重试抖动
- **双向预警**：上涨和下跌都触发（暴跌=衰退/信用危机）
- **三级预警**：🟡 黄色 → 🟠 橙色 → 🔴 红色 → 🔴🔴 共振
- **走势图**：QuickChart 自动生成 PNG + 可点击 URL
- **零依赖**：纯 Python 标准库，无需 pip install
- **三种运行模式**：直连 / 管道 / 混合（stdin + fallback）

### 预警阈值

| 指标 | 🟡 | 🟠 | 🔴 |
|------|-----|-----|-----|
| 美债10Y | ±20bp | ±30bp | ±50bp 或 ≥5.0% 或 ≤3.5% |
| 美元指数 | ±0.5% | ±1.0% | ±1.5% 或 ≥105 或 ≤98 |

### 数据源

| 优先级 | 源 | 接口 |
|--------|-----|------|
| 1 | 东方财富 push2 | `push2.eastmoney.com/api/qt/stock/get` |
| 2 | 东方财富 K线 | `push2his.eastmoney.com/api/qt/stock/kline/get` |
| 3 | 新浪财经 | `hq.sinajs.cn` |

## Usage

Skills auto-trigger on relevant keywords.

```
User: "add export feature"
Agent: Plan → Diagnose → Implement → Verify → Sync → Ship  (dev-flow)

User: "部署金融危机监控"
Agent: 复制脚本 → 生成cron配置 → 注册定时任务  (fin-crisis-monitor)

User: "新建项目"
Agent: 9 阶段脚手架 + 多工具配置 + 记忆资产 + 纪律门禁  (harness-project-init)
```
