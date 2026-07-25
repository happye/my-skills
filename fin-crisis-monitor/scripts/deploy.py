#!/usr/bin/env python3
"""
金融危机地基信号监控 — 一键部署脚本
用法：python deploy.py [--workspace PATH] [--wechat-id ID] [--dry-run]

功能：
1. 复制 fin_crisis_monitor.py 到 workspace/scripts/
2. 创建 3 个 cron 任务（早6/午14/晚20）
3. （可选）发一条测试消息验证微信通道

参数：
  --workspace PATH   OpenClaw workspace 路径（默认 C:\Users\Crux\.qclaw\workspace）
  --wechat-id ID     微信推送目标 ID（默认使用已知 ID）
  --dry-run          只打印将要做的事，不实际执行
"""
import sys
import os
import json
import shutil

# 默认配置
DEFAULT_WORKSPACE = r"C:\Users\Crux\.qclaw\workspace"
DEFAULT_WECHAT_ID = "o9cq804BxrvfMtjVDCN2kMqes6L0@im.wechat"
SCRIPT_NAME = "fin_crisis_monitor.py"
DATA_NAME = "fin_crisis_data.json"

# Cron 任务配置
CRON_JOBS = [
    {
        "name": "早间风险信号汇总",
        "schedule": {"kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Shanghai"},
        "time_label": "早间",
        "focus_word": "今日",
    },
    {
        "name": "午间风险信号汇总",
        "schedule": {"kind": "cron", "expr": "0 14 * * *", "tz": "Asia/Shanghai"},
        "time_label": "午间",
        "focus_word": "今日",
    },
    {
        "name": "晚间风险信号汇总",
        "schedule": {"kind": "cron", "expr": "0 20 * * *", "tz": "Asia/Shanghai"},
        "time_label": "晚间",
        "focus_word": "今晚",
    },
]


def generate_prompt(time_label, focus_word, workspace_path, wechat_id):
    """生成 cron 任务的 prompt"""
    script_path = workspace_path.replace("\\", "\\\\") + r"\\scripts\\fin_crisis_monitor.py"
    # PowerShell 转义
    script_path_exec = workspace_path + r"\scripts\fin_crisis_monitor.py"

    return f"""执行{time_label}风险信号汇总。

## 第一步：地基信号监控（美债 + 美元指数）

### 数据获取（两步法）

步骤A：用 web_fetch 工具同时获取两个东方财富API数据：
- 美债：https://push2.eastmoney.com/api/qt/stock/get?secid=171.US10Y&fields=f43,f44,f45,f46,f57,f58,f170
- 美元：https://push2.eastmoney.com/api/qt/stock/get?secid=100.UDI&fields=f43,f44,f45,f46,f57,f58,f170

从每个返回的JSON中提取 data 对象（含 f43,f44,f45,f46,f170 等字段），构造一个JSON字符串：
{{"us10y":{{美债的data对象}},"udi":{{美元的data对象}}}}

步骤B：将JSON通过管道传给Python脚本（混合模式，stdin失败会自动直连）：
用 exec 执行：echo '构造的JSON' | python {script_path_exec} --stdin --fallback

如果 web_fetch 也失败，直接用 exec 运行：python {script_path_exec}
（脚本有3层数据源+3次重试+随机延迟反爬）

### 解析脚本输出
脚本输出JSON，关键字段：
- current.us10y.value：收益率百分比
- current.udi.value：美元指数
- changes.us10y.daily_bp：日内基点变动（正=上涨，负=下跌）
- changes.udi.daily_pct：日内变动
- alerts：预警数组（可能为空）
- has_alert：是否有预警
- charts.us10y_url / charts.udi_url：QuickChart走势图URL
- charts.us10y_path / charts.udi_path：本地PNG路径

## 第二步：新闻风险信号汇总

1. 读 risk-radar-master skill（~/.qclaw/skills/risk-radar-master/SKILL.md）
2. 读 risk-radar-content-production skill
3. 按skill流程：分层搜索新闻→后台深度分析→前台极简输出
4. 读 risk-radar-review-compliance skill 做最终合规审查

## 输出格式（强制，不可变）

先放地基信号，再放新闻风险信号，最后放走势图链接。

[如果有预警，在最前面：]
[预警emoji] 地基信号警报
美债10年收益率 X.XXX%（日内+/-Xbp，3日+/-Xbp，5日+/-Xbp）
美元指数 XX.XX（日内+/-X.XX%，3日+/-X.XX%，5日+/-X.XX%）
[警报详情]
---

[新闻风险信号]
🔴/🟡/🟢 标题
正文2-3行，说清楚现象、机制、需要关注什么。
（重复3-6条，每条之间空一行）
---

{focus_word}重点盯的公开信号：
- 条目1
- 条目2
- 条目3
---

[如果没有预警：]
地基信号：美债10年收益率 X.XXX%（日内+/-Xbp），美元指数 XX.XX（日内+/-X.XX%），暂无异常
---

[新闻风险信号（同上）]
---

走势图：
美债收益率：charts.us10y_url的值
美元指数：charts.udi_url的值

以上基于公开信息整理，不构成投资建议。

## 发送
用 message 工具一次性发送完整文字汇总（含走势图URL）：
message(action="send", channel="wechat-access", to="{wechat_id}", message="完整汇总文字")

## 禁止
- 表格、多级标题、每次改变格式
- 不要写入任何本地文件（Python脚本管理数据文件）
- 不要发送图片文件（wechat-access不支持media），用URL代替
- 不要省略走势图URL（即使charts为null也要写'走势图暂不可用'）"""


def main():
    workspace = DEFAULT_WORKSPACE
    wechat_id = DEFAULT_WECHAT_ID
    dry_run = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--workspace" and i + 1 < len(args):
            workspace = args[i + 1]; i += 2
        elif args[i] == "--wechat-id" and i + 1 < len(args):
            wechat_id = args[i + 1]; i += 2
        elif args[i] == "--dry-run":
            dry_run = True; i += 1
        else:
            print(f"未知参数: {args[i]}"); i += 1

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("金融危机地基信号监控 — 一键部署")
    print("=" * 60)
    print(f"Workspace:  {workspace}")
    print(f"微信目标ID: {wechat_id}")
    print(f"脚本源目录: {script_dir}")
    print(f"Dry run:    {dry_run}")
    print()

    # Step 1: 复制脚本
    src_script = os.path.join(script_dir, SCRIPT_NAME)
    dst_dir = os.path.join(workspace, "scripts")
    dst_script = os.path.join(dst_dir, SCRIPT_NAME)

    print(f"[1/3] 复制脚本 → {dst_script}")
    if not os.path.exists(src_script):
        print(f"  ❌ 源文件不存在: {src_script}")
        sys.exit(1)

    if dry_run:
        print("  (dry-run) 跳过实际复制")
    else:
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src_script, dst_script)
        print(f"  ✅ 已复制 ({os.path.getsize(dst_script)} bytes)")

    # Step 2: 生成 cron 任务配置 JSON
    print(f"\n[2/3] 生成 cron 任务配置")
    cron_configs = []
    for job in CRON_JOBS:
        prompt = generate_prompt(
            job["time_label"], job["focus_word"],
            workspace, wechat_id
        )
        config = {
            "name": job["name"],
            "schedule": job["schedule"],
            "sessionTarget": "isolated",
            "wakeMode": "now",
            "payload": {
                "kind": "agentTurn",
                "message": prompt
            },
            "delivery": {"mode": "none"}
        }
        cron_configs.append(config)
        print(f"  📋 {job['name']} — {job['schedule']['expr']} ({job['schedule']['tz']})")

    config_path = os.path.join(script_dir, "cron_configs.json")
    if dry_run:
        print(f"  (dry-run) 配置未写入，将写入: {config_path}")
    else:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cron_configs, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 配置已写入: {config_path}")

    # Step 3: 输出 cron 工具调用命令
    print(f"\n[3/3] Cron 任务注册指令")
    print("-" * 60)
    print("以下 JSON 可直接用于 cron 工具 add 操作，")
    print("或由 agent 自动执行 cron(action='add', job=<每个config>)")
    print("-" * 60)

    for i, config in enumerate(cron_configs):
        print(f"\n--- 任务 {i+1}/{len(cron_configs)}: {config['name']} ---")
        print(json.dumps(config, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    if dry_run:
        print("Dry run 完成。去掉 --dry-run 实际执行。")
    else:
        print("✅ 部署文件准备完毕。")
        print()
        print("下一步（由 agent 自动执行）：")
        print("  对每个 cron config 调用 cron(action='add', job=config)")
        print()
        print("或手动在 OpenClaw 中创建 cron 任务。")
    print("=" * 60)


if __name__ == "__main__":
    main()
