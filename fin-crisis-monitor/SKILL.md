---
name: fin-crisis-monitor
description: 金融危机地基信号监控。定时获取美债10年收益率和美元指数，计算趋势变动，分级预警，生成走势图，通过微信推送。支持多数据源容错、反爬策略、双向预警。
---

# 金融危机地基信号监控

监控美债10年收益率 + 美元指数两大"地基信号"，定时获取数据、计算趋势、分级预警，生成走势图并推送。

## 一键部署

```bash
# 1. 复制脚本到 workspace
cp scripts/fin_crisis_monitor.py <workspace>/scripts/

# 2. 运行部署脚本（生成 cron 配置）
python scripts/deploy.py --workspace <workspace> --wechat-id <你的微信ID>

# 3. 用 cron 工具注册 3 个定时任务
# （deploy.py 会输出可直接使用的 cron job JSON）
```

参数：
- `--workspace PATH` — OpenClaw workspace 路径（默认 `C:\Users\Crux\.qclaw\workspace`）
- `--wechat-id ID` — 微信推送目标 ID
- `--dry-run` — 预览不执行

## 核心脚本：fin_crisis_monitor.py

### 运行模式

| 模式 | 命令 | 说明 |
|------|------|------|
| 直连 | `python fin_crisis_monitor.py` | 3层多数据源 + 重试 + 反爬 |
| 管道 | `echo '{json}' \| python fin_crisis_monitor.py --stdin` | 接收 web_fetch 获取的数据 |
| 混合 | `echo '{json}' \| python fin_crisis_monitor.py --stdin --fallback` | stdin 优先，失败自动直连 |

### 数据源优先级

| 优先级 | 数据源 | 美债 | 美元指数 |
|--------|--------|------|----------|
| 1 | 东方财富 push2 | secid=171.US10Y | secid=100.UDI |
| 2 | 东方财富 push2his K线 | 近7天K线 | 近7天K线 |
| 3 | 新浪财经 | gb_$ust10y | fx_susdx |

### 反爬策略
- 5个 User-Agent 轮换
- 请求间随机延迟 0.5-2.0 秒
- 重试间隔加 0-2 秒随机抖动
- Referer 头模拟浏览器

### 预警阈值（双向）

| 级别 | 美债变动 | 美元变动 | 说明 |
|------|----------|----------|------|
| 🟡 黄色 | ≥20bp | ≥0.5% | 单日异动 |
| 🟠 橙色 | ≥30bp | ≥1.0% | 或3日趋势 ≥40bp/3% |
| 🔴 红色 | ≥50bp | ≥1.5% | 或5日趋势 ≥60bp/5%，或绝对水平突破 |
| 🔴🔴 共振 | — | — | 美债+美元同时异动 |

- 美债收益率 ≥5.0% → 红色警报（地基通胀）
- 美债收益率 ≤3.5% → 红色警报（衰退信号）
- 美元指数 ≥105 → 红色警报（美元过强）
- 美元指数 ≤98 → 红色警报（信用危机）
- **下跌也预警**，不只是上涨

### 走势图
- QuickChart POST 下载 PNG 到本地
- 同时生成 GET URL（微信可显示为可点击链接）
- PNG 校验文件头（\x89PNG）
- 不足3条历史数据时跳过图表

## 东方财富 API 字段

| 字段 | 含义 | 美债除数 | 美元除数 |
|------|------|----------|----------|
| f43 | 最新价 | 10000 | 100 |
| f44 | 最高价 | 10000 | 100 |
| f45 | 最低价 | 10000 | 100 |
| f46 | 开盘价 | 10000 | 100 |
| f57 | 代码 | — | — |
| f58 | 名称 | — | — |
| f170 | 涨跌幅(%) | 100 | 100 |

## 历史数据

`fin_crisis_data.json` 保存在脚本同目录，自动管理：
- 保留最近30天
- 同一天多次运行更新当日记录
- 兼容旧格式（仅有 value 字段的记录）

## Cron 任务

三个定时任务（早6/午14/晚20），由 `deploy.py` 自动生成配置：

| 任务 | 时间 | 时区 |
|------|------|------|
| 早间 | 0 6 * * * | Asia/Shanghai |
| 午间 | 0 14 * * * | Asia/Shanghai |
| 晚间 | 0 20 * * * | Asia/Shanghai |

每个任务：
1. 用 web_fetch 获取东方财富 API 数据
2. 管道传入脚本（混合模式）
3. 解析输出 JSON
4. 搜索新闻风险信号（可选）
5. 通过微信推送汇总
