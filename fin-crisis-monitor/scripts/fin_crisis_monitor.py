#!/usr/bin/env python3
"""
金融危机地基信号监控脚本 v2
监控美债10年收益率 + 美元指数

支持三种模式：
1. 直连模式（默认）：python fin_crisis_monitor.py
   脚本直接拉取多数据源API（带反爬策略）
2. 管道模式：python fin_crisis_monitor.py --stdin < data.json
   接收 agent 通过 web_fetch 获取的原始 JSON 数据
3. 混合模式：python fin_crisis_monitor.py --stdin < data.json --fallback
   先用 stdin 数据，失败则自动直连

数据源优先级（直连模式）：
  美债10Y: 东方财富push2 → 新浪财经 → 金十数据网页
  美元指数: 东方财富push2 → 新浪财经 → 金十数据网页

输出：JSON 格式的预警分析结果
"""
import json
import os
import sys
import time
import random
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta

# ============================================================
# 数据源配置
# ============================================================

# 东方财富 push2 API（主源）
EM_US10Y_URL = "https://push2.eastmoney.com/api/qt/stock/get?secid=171.US10Y&fields=f43,f44,f45,f46,f57,f58,f170"
EM_UDI_URL = "https://push2.eastmoney.com/api/qt/stock/get?secid=100.UDI&fields=f43,f44,f45,f46,f57,f58,f170"
# 东方财富 push2his（K线历史，备用）——动态计算最近7天范围
_now = datetime.now(timezone(timedelta(hours=8)))
_beg_date = (_now - timedelta(days=7)).strftime("%Y%m%d")
_end_date = _now.strftime("%Y%m%d")
EM_HIS_US10Y_URL = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=171.US10Y&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&beg={_beg_date}&end={_end_date}&lmt=5"
EM_HIS_UDI_URL = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=100.UDI&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&beg={_beg_date}&end={_end_date}&lmt=5"

# 新浪财经（备用源1）
SINA_US10Y_URL = "https://hq.sinajs.cn/list=gb_$ust10y"
SINA_UDI_URL = "https://hq.sinajs.cn/list=fx_susdx"

# 历史数据文件
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fin_crisis_data.json")

# ============================================================
# 预警阈值
# ============================================================

THRESHOLDS = {
    "us10y": {
        "yellow": 20,    # 单日变动 >=20bp
        "orange": 30,    # 单日变动 >=30bp
        "red": 50,       # 单日变动 >=50bp 或突破5.0% 或跌破3.5%
        "trend_3d": 40,  # 3日累计变动 >=40bp
        "trend_5d": 60,  # 5日累计变动 >=60bp
        "level_red_high": 5.0,   # 收益率绝对值突破5.0%
        "level_red_low": 3.5     # 收益率绝对值跌破3.5%（衰退信号）
    },
    "udi": {
        "yellow": 0.5,   # 单日变动 >=0.5%
        "orange": 1.0,   # 单日变动 >=1.0%
        "red": 1.5,      # 单日变动 >=1.5% 或突破105或跌破98
        "trend_3d": 3.0, # 3日累计变动 >=3%
        "trend_5d": 5.0, # 5日累计变动 >=5%
        "level_red_high": 105,  # 美元指数绝对值突破105
        "level_red_low": 98     # 美元指数绝对值跌破98
    }
}

# ============================================================
# 网络请求配置
# ============================================================

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]  # 重试间隔（秒）
REQUEST_TIMEOUT = 15  # 请求超时（秒）

# 反爬策略：随机延迟 + 轮换UA
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def get_random_ua():
    return random.choice(USER_AGENTS)


def anti_crawl_delay():
    """随机延迟 0.5~2 秒，避免触发反爬"""
    time.sleep(random.uniform(0.5, 2.0))


def http_get(url, extra_headers=None, timeout=REQUEST_TIMEOUT):
    """带重试 + 反爬策略的 HTTP GET"""
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://quote.eastmoney.com/",
    }
    if extra_headers:
        headers.update(extra_headers)

    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            anti_crawl_delay()  # 每次请求前随机延迟
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt] + random.uniform(0, 2)
                print(f"  [重试 {attempt+1}/{MAX_RETRIES}] {type(e).__name__}: {e}，{delay:.1f}s后重试...", file=sys.stderr)
                time.sleep(delay)
    raise last_err


def http_post_json(url, body, timeout=30):
    """带重试的 HTTP POST JSON"""
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            anti_crawl_delay()
            post_data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url, data=post_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": get_random_ua(),
                    "Accept": "image/png, */*",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt] + random.uniform(0, 2)
                print(f"  [重试 {attempt+1}/{MAX_RETRIES}] {type(e).__name__}: {e}，{delay:.1f}s后重试...", file=sys.stderr)
                time.sleep(delay)
    raise last_err


# ============================================================
# 数据解析器
# ============================================================

def parse_eastmoney(text, is_us10y):
    """解析东方财富 push2 API 返回"""
    data = json.loads(text)
    if data.get("rc") != 0 or not data.get("data"):
        raise ValueError(f"东方财富API返回异常: rc={data.get('rc')}")
    d = data["data"]
    divisor = 10000 if is_us10y else 100
    value = d["f43"] / divisor
    # 校验数值合理性
    if is_us10y and not (0 < value < 20):
        raise ValueError(f"美债收益率数值异常: {value}")
    if not is_us10y and not (50 < value < 200):
        raise ValueError(f"美元指数数值异常: {value}")
    return {
        "value": value,
        "high": d.get("f44", d["f43"]) / divisor,
        "low": d.get("f45", d["f43"]) / divisor,
        "open": d.get("f46", d["f43"]) / divisor,
        "change_pct": d.get("f170", 0) / 100,
        "name": d.get("f58", ""),
        "ts": _now_iso()
    }


def parse_eastmoney_kline(text, is_us10y):
    """解析东方财富 push2his K线API返回（备用）"""
    data = json.loads(text)
    if data.get("rc") != 0 or not data.get("data"):
        raise ValueError(f"东方财富K线API返回异常: rc={data.get('rc')}")
    d = data["data"]
    klines = d.get("klines", [])
    if not klines:
        raise ValueError("东方财富K线无数据")
    # 格式: "date,open,close,high,low,volume,amount"
    last = klines[-1]
    parts = last.split(",")
    if len(parts) < 5:
        raise ValueError(f"K线数据格式异常: {last}")
    close = float(parts[2])
    open_val = float(parts[1])
    high = float(parts[3])
    low = float(parts[4])
    # 校验
    if is_us10y and not (0 < close < 20):
        raise ValueError(f"美债收益率K线数值异常: {close}")
    if not is_us10y and not (50 < close < 200):
        raise ValueError(f"美元指数K线数值异常: {close}")
    change_pct = ((close - open_val) / open_val * 100) if open_val else 0
    return {
        "value": close,
        "high": high,
        "low": low,
        "open": open_val,
        "change_pct": round(change_pct, 2),
        "name": d.get("name", ""),
        "ts": _now_iso()
    }


def parse_sina(text, name, is_us10y):
    """解析新浪财经 API 返回（备用源）

    新浪返回格式：var hq_str_gb_$ust10y="名称,开盘,最新价,涨跌额,涨跌幅,...";
    新浪返回格式：var hq_str_fx_susdx="名称,开盘,最新价,涨跌额,涨跌幅,...";
    """
    if "=" not in text or '"' not in text:
        raise ValueError("新浪API返回格式异常")
    content = text.split('"')[1] if '"' in text else ""
    if not content:
        raise ValueError("新浪API返回内容为空")
    parts = content.split(",")
    parts = [p.strip() for p in parts]
    if len(parts) < 3:
        raise ValueError(f"新浪API字段不足: {content[:100]}")

    # 新浪格式: [0]=名称, [1]=开盘, [2]=最新价
    try:
        open_val = float(parts[1]) if parts[1] else 0
        value = float(parts[2]) if parts[2] else 0
    except (ValueError, IndexError) as e:
        raise ValueError(f"新浪API数值解析失败: {e}, content={content[:100]}")

    if value <= 0:
        raise ValueError(f"新浪API数值无效: {value}")

    # 校验数值合理性
    if is_us10y and not (0 < value < 20):
        raise ValueError(f"美债收益率新浪数值异常: {value}")
    if not is_us10y and not (50 < value < 200):
        raise ValueError(f"美元指数新浪数值异常: {value}")

    change_pct = ((value - open_val) / open_val * 100) if open_val else 0
    return {
        "value": value,
        "high": value,
        "low": value,
        "open": open_val if open_val else value,
        "change_pct": round(change_pct, 2),
        "name": parts[0] if parts[0] else name,
        "ts": _now_iso()
    }


def _now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


# ============================================================
# 数据获取
# ============================================================

def fetch_one_direct(name, is_us10y):
    """直连模式：多数据源逐个尝试获取单个指标

    数据源优先级：
    1. 东方财富 push2（实时报价）
    2. 东方财富 push2his（K线历史，取最新一条）
    3. 新浪财经
    """
    if is_us10y:
        sources = [
            ("eastmoney", EM_US10Y_URL, lambda t: parse_eastmoney(t, True), {}),
            ("eastmoney_kline", EM_HIS_US10Y_URL, lambda t: parse_eastmoney_kline(t, True), {}),
            ("sina", SINA_US10Y_URL, lambda t: parse_sina(t, name, True), {"Referer": "https://finance.sina.com.cn"}),
        ]
    else:
        sources = [
            ("eastmoney", EM_UDI_URL, lambda t: parse_eastmoney(t, False), {}),
            ("eastmoney_kline", EM_HIS_UDI_URL, lambda t: parse_eastmoney_kline(t, False), {}),
            ("sina", SINA_UDI_URL, lambda t: parse_sina(t, name, False), {"Referer": "https://finance.sina.com.cn"}),
        ]

    errors = []
    for source_name, url, parser, extra_headers in sources:
        try:
            text = http_get(url, extra_headers=extra_headers if extra_headers else None)
            data = parser(text)
            data["_source"] = source_name
            print(f"  [{name}] 数据源 {source_name} 成功", file=sys.stderr)
            return data
        except Exception as e:
            err = f"{source_name}: {type(e).__name__}: {e}"
            errors.append(err)
            print(f"  [{name}] 数据源 {source_name} 失败: {err}", file=sys.stderr)

    return {"error": f"所有数据源失败: {' / '.join(errors)}"}


def fetch_data_direct():
    """直连模式：获取美债 + 美元指数"""
    results = {}
    for name, is_us10y in [("us10y", True), ("udi", False)]:
        results[name] = fetch_one_direct(name, is_us10y)
    return results


def fetch_data_stdin():
    """管道模式：从 stdin 读取 agent 通过 web_fetch 获取的原始 JSON 数据

    期望输入格式（JSON）：
    {
      "us10y": {"f43": 46872, "f44": 47135, "f45": 46527, "f46": 46972, "f170": -21, "f58": "..."},
      "udi": {"f43": 10133, "f44": 10146, "f45": 10125, "f46": 10144, "f170": -11, "f58": "..."}
    }

    或东方财富原始格式：
    {
      "us10y": {"rc":0,"data":{"f43":46872,...}},
      "udi": {"rc":0,"data":{"f43":10133,...}}
    }
    """
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("stdin 无数据")

    input_data = json.loads(raw)
    results = {}

    for name, is_us10y in [("us10y", True), ("udi", False)]:
        if name not in input_data:
            results[name] = {"error": f"缺少 {name} 数据"}
            continue

        raw_item = input_data[name]

        # 处理东方财富原始格式
        if isinstance(raw_item, dict) and "data" in raw_item and "rc" in raw_item:
            raw_item = raw_item["data"]

        # 处理 web_fetch 包装格式（字符串中嵌套JSON）
        if isinstance(raw_item, str):
            try:
                raw_item = json.loads(raw_item)
            except json.JSONDecodeError:
                if "{" in raw_item:
                    start = raw_item.index("{")
                    end = raw_item.rindex("}") + 1
                    try:
                        raw_item = json.loads(raw_item[start:end])
                    except json.JSONDecodeError:
                        results[name] = {"error": f"{name} JSON解析失败"}
                        continue
                else:
                    results[name] = {"error": f"{name} 数据格式异常: {str(raw_item)[:200]}"}
                    continue

        if not isinstance(raw_item, dict) or "f43" not in raw_item:
            results[name] = {"error": f"{name} 缺少f43字段: {str(raw_item)[:200]}"}
            continue

        divisor = 10000 if is_us10y else 100
        d = raw_item
        value = d["f43"] / divisor

        # 数值校验
        if is_us10y and not (0 < value < 20):
            results[name] = {"error": f"{name} 数值异常: {value}"}
            continue
        if not is_us10y and not (50 < value < 200):
            results[name] = {"error": f"{name} 数值异常: {value}"}
            continue

        results[name] = {
            "value": value,
            "high": d.get("f44", d["f43"]) / divisor,
            "low": d.get("f45", d["f43"]) / divisor,
            "open": d.get("f46", d["f43"]) / divisor,
            "change_pct": d.get("f170", 0) / 100,
            "name": d.get("f58", name),
            "ts": _now_iso(),
            "_source": "web_fetch"
        }

    return results


def fetch_data_hybrid():
    """混合模式：先用 stdin 数据，失败的指标自动直连获取"""
    try:
        current = fetch_data_stdin()
    except Exception as e:
        print(f"  stdin 读取失败: {e}，切换到直连模式", file=sys.stderr)
        return fetch_data_direct()

    for name in ["us10y", "udi"]:
        if "error" in current.get(name, {}):
            print(f"  [{name}] stdin 数据异常，尝试直连...", file=sys.stderr)
            direct_data = fetch_one_direct(name, name == "us10y")
            if "error" not in direct_data:
                current[name] = direct_data

    return current


# ============================================================
# 历史数据管理
# ============================================================

def load_history():
    """加载历史数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"records": []}


def save_history(history):
    """保存历史数据，只保留最近30天"""
    cutoff = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=30)
    cutoff_str = cutoff.isoformat()
    history["records"] = [
        r for r in history["records"]
        if r.get("ts", "") >= cutoff_str
    ]
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"  历史数据保存失败: {e}", file=sys.stderr)


def get_today_record(history):
    """获取今天的记录（如果已存在）"""
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    for r in history["records"]:
        if r.get("ts", "").startswith(today):
            return r
    return None


# ============================================================
# 变动计算 & 预警
# ============================================================

def _safe_get_value(record, key):
    """安全获取历史记录中的值，兼容旧格式（只有 value 字段）"""
    entry = record.get(key)
    if entry is None:
        return None
    if isinstance(entry, dict):
        return entry.get("value")
    return None


def calc_changes(history, current):
    """计算日内变动和趋势

    日内变动：今天的值 vs 昨天最后一条记录的值
    3日趋势：今天的值 vs 3个交易日前记录的值
    5日趋势：今天的值 vs 5个交易日前记录的值
    """
    result = {
        "us10y": {"daily_bp": 0, "trend_3d_bp": 0, "trend_5d_bp": 0},
        "udi": {"daily_pct": 0, "trend_3d_pct": 0, "trend_5d_pct": 0}
    }

    records = history.get("records", [])
    if not records:
        return result

    today_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    # 排除今天的记录，只看历史
    prev_records = [r for r in records if not r.get("ts", "").startswith(today_str)]

    if prev_records:
        last = prev_records[-1]
        u10y_prev = _safe_get_value(last, "us10y")
        udi_prev = _safe_get_value(last, "udi")
        cur_u10y = current["us10y"]["value"]
        cur_udi = current["udi"]["value"]

        if u10y_prev is not None and u10y_prev > 0:
            result["us10y"]["daily_bp"] = round((cur_u10y - u10y_prev) * 100, 1)
        if udi_prev is not None and udi_prev > 0:
            result["udi"]["daily_pct"] = round(cur_udi - udi_prev, 2)

    # 3日趋势：取倒数第3条历史记录
    if len(prev_records) >= 3:
        ref = prev_records[-3]
        u10y_ref = _safe_get_value(ref, "us10y")
        udi_ref = _safe_get_value(ref, "udi")
        cur_u10y = current["us10y"]["value"]
        cur_udi = current["udi"]["value"]

        if u10y_ref is not None and u10y_ref > 0:
            result["us10y"]["trend_3d_bp"] = round((cur_u10y - u10y_ref) * 100, 1)
        if udi_ref is not None and udi_ref > 0:
            result["udi"]["trend_3d_pct"] = round(cur_udi - udi_ref, 2)

    # 5日趋势：取倒数第5条历史记录
    if len(prev_records) >= 5:
        ref = prev_records[-5]
        u10y_ref = _safe_get_value(ref, "us10y")
        udi_ref = _safe_get_value(ref, "udi")
        cur_u10y = current["us10y"]["value"]
        cur_udi = current["udi"]["value"]

        if u10y_ref is not None and u10y_ref > 0:
            result["us10y"]["trend_5d_bp"] = round((cur_u10y - u10y_ref) * 100, 1)
        if udi_ref is not None and udi_ref > 0:
            result["udi"]["trend_5d_pct"] = round(cur_udi - udi_ref, 2)

    return result


def check_alerts(current, changes):
    """检查预警（双向：上涨和下跌都是风险信号）"""
    alerts = []

    # --- 美债收益率 ---
    u = changes["us10y"]
    cv = current["us10y"]["value"]
    t = THRESHOLDS["us10y"]
    abs_daily = abs(u["daily_bp"])
    abs_3d = abs(u["trend_3d_bp"])
    abs_5d = abs(u["trend_5d_bp"])

    # 绝对水平预警
    if cv >= t["level_red_high"]:
        alerts.append(("🔴", f"美债10年收益率突破{t['level_red_high']}%，当前 {cv:.3f}%，地基级别警报"))
    elif cv <= t["level_red_low"]:
        alerts.append(("🔴", f"美债10年收益率跌破{t['level_red_low']}%，当前 {cv:.3f}%，衰退信号警报"))

    # 单日变动预警（双向）
    elif abs_daily >= t["red"]:
        direction = "飙升" if u["daily_bp"] > 0 else "暴跌"
        alerts.append(("🔴", f"美债收益率单日{direction} {abs_daily}bp，当前 {cv:.3f}%，红色警报"))
    elif abs_daily >= t["orange"]:
        direction = "上涨" if u["daily_bp"] > 0 else "下跌"
        alerts.append(("🟠", f"美债收益率单日{direction} {abs_daily}bp，当前 {cv:.3f}%，橙色警报"))
    elif abs_daily >= t["yellow"]:
        direction = "上涨" if u["daily_bp"] > 0 else "下跌"
        alerts.append(("🟡", f"美债收益率单日{direction} {abs_daily}bp，当前 {cv:.3f}%，黄色提醒"))

    # 趋势预警（双向）
    if abs_3d >= t["trend_3d"]:
        direction = "上行" if u["trend_3d_bp"] > 0 else "下行"
        alerts.append(("🟠", f"美债收益率3日累计{direction} {abs_3d}bp，趋势性异动"))
    if abs_5d >= t["trend_5d"]:
        direction = "上行" if u["trend_5d_bp"] > 0 else "下行"
        alerts.append(("🔴", f"美债收益率5日累计{direction} {abs_5d}bp，持续异动"))

    # --- 美元指数 ---
    d = changes["udi"]
    dv = current["udi"]["value"]
    t = THRESHOLDS["udi"]
    abs_daily_d = abs(d["daily_pct"])
    abs_3d_d = abs(d["trend_3d_pct"])
    abs_5d_d = abs(d["trend_5d_pct"])

    # 绝对水平预警
    if dv >= t["level_red_high"]:
        alerts.append(("🔴", f"美元指数突破{t['level_red_high']}，当前 {dv:.2f}，地基级别警报"))
    elif dv <= t["level_red_low"]:
        alerts.append(("🔴", f"美元指数跌破{t['level_red_low']}，当前 {dv:.2f}，美元信用危机警报"))

    # 单日变动预警（双向）
    elif abs_daily_d >= t["red"]:
        direction = "暴涨" if d["daily_pct"] > 0 else "暴跌"
        alerts.append(("🔴", f"美元指数单日{direction} {abs_daily_d:.2f}%，当前 {dv:.2f}，红色警报"))
    elif abs_daily_d >= t["orange"]:
        direction = "上涨" if d["daily_pct"] > 0 else "下跌"
        alerts.append(("🟠", f"美元指数单日{direction} {abs_daily_d:.2f}%，当前 {dv:.2f}，橙色警报"))
    elif abs_daily_d >= t["yellow"]:
        direction = "上涨" if d["daily_pct"] > 0 else "下跌"
        alerts.append(("🟡", f"美元指数单日{direction} {abs_daily_d:.2f}%，当前 {dv:.2f}，黄色提醒"))

    # 趋势预警（双向）
    if abs_3d_d >= t["trend_3d"]:
        direction = "走强" if d["trend_3d_pct"] > 0 else "走弱"
        alerts.append(("🟠", f"美元指数3日累计{direction} {abs_3d_d:.2f}%，趋势性异动"))
    if abs_5d_d >= t["trend_5d"]:
        direction = "走强" if d["trend_5d_pct"] > 0 else "走弱"
        alerts.append(("🔴", f"美元指数5日累计{direction} {abs_5d_d:.2f}%，持续异动"))

    # --- 共振预警 ---
    u_alert = abs_daily >= t["yellow"] or abs_3d >= t["trend_3d"]
    d_alert = abs_daily_d >= t["yellow"] or abs_3d_d >= t["trend_3d"]
    if u_alert and d_alert:
        alerts.append(("🔴🔴", "美债收益率 + 美元指数同时异动，地基与闸门同时动摇，最高级别警报！"))

    return alerts


# ============================================================
# 图表生成
# ============================================================

def generate_charts(history):
    """生成 QuickChart 走势图：下载 PNG 到本地 + 生成可点击 URL"""
    records = history.get("records", [])
    if len(records) < 3:
        print("  历史数据不足3条，跳过图表生成", file=sys.stderr)
        return None

    recent = records[-10:]
    dates = []
    us10y_vals = []
    udi_vals = []

    for r in recent:
        ts = r.get("ts", "")
        date_str = ts[5:10].replace("-", "/")
        dates.append(date_str)
        u10y_val = _safe_get_value(r, "us10y")
        udi_val = _safe_get_value(r, "udi")
        if u10y_val is None or udi_val is None:
            continue
        us10y_vals.append(round(u10y_val, 3))
        udi_vals.append(round(udi_val, 2))

    if len(us10y_vals) < 3:
        print("  有效数据不足3条，跳过图表生成", file=sys.stderr)
        return None

    # 美债收益率走势图配置
    us10y_config = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": [{
                "label": "US 10Y Yield (%)",
                "data": us10y_vals,
                "borderColor": "#e74c3c",
                "backgroundColor": "rgba(231, 76, 60, 0.1)",
                "fill": True,
                "pointRadius": 4,
                "pointBackgroundColor": "#e74c3c",
                "borderWidth": 2,
                "tension": 0.3
            }]
        },
        "options": {
            "title": {"display": True, "text": "US 10Y Treasury Yield (%)", "fontSize": 16},
            "legend": {"display": False},
            "scales": {"yAxes": [{"ticks": {"min": round(min(us10y_vals) - 0.1, 2), "max": round(max(us10y_vals) + 0.1, 2)}}]},
            "plugins": {"datalabels": {"display": True, "anchor": "end", "align": "top", "font": {"size": 11}, "color": "#333"}}
        }
    }

    # 美元指数走势图配置
    udi_config = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": [{
                "label": "Dollar Index (DXY)",
                "data": udi_vals,
                "borderColor": "#2980b9",
                "backgroundColor": "rgba(52, 152, 219, 0.1)",
                "fill": True,
                "pointRadius": 4,
                "pointBackgroundColor": "#2980b9",
                "borderWidth": 2,
                "tension": 0.3
            }]
        },
        "options": {
            "title": {"display": True, "text": "US Dollar Index (DXY)", "fontSize": 16},
            "legend": {"display": False},
            "scales": {"yAxes": [{"ticks": {"min": round(min(udi_vals) - 0.5, 1), "max": round(max(udi_vals) + 0.5, 1)}}]},
            "plugins": {"datalabels": {"display": True, "anchor": "end", "align": "top", "font": {"size": 11}, "color": "#333"}}
        }
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))

    result = {
        "us10y_url": None, "udi_url": None,
        "us10y_path": None, "udi_path": None
    }

    for name, config in [
        ("us10y", us10y_config),
        ("udi", udi_config),
    ]:
        # 生成可点击的 GET URL
        config_str = json.dumps(config, ensure_ascii=False)
        chart_url = "https://quickchart.io/chart?w=600&h=300&c=" + urllib.parse.quote(config_str, safe='')
        result[f"{name}_url"] = chart_url

        # 同时下载 PNG 到本地（带重试）
        path = os.path.join(script_dir, f"chart_{name}.png")
        try:
            post_body = {"chart": config, "width": 600, "height": 300, "format": "png"}
            img_data = http_post_json("https://quickchart.io/chart", post_body, timeout=30)
            # 校验返回的是有效图片（PNG 文件头: \x89PNG）
            if img_data and len(img_data) > 100 and img_data[:4] == b'\x89PNG':
                with open(path, "wb") as f:
                    f.write(img_data)
                result[f"{name}_path"] = path
                print(f"  [{name}] 图表PNG下载成功: {path}", file=sys.stderr)
            else:
                raise ValueError(f"返回数据不是有效PNG (len={len(img_data) if img_data else 0})")
        except Exception as e:
            print(f"  [{name}] 图表PNG下载失败: {type(e).__name__}: {e}", file=sys.stderr)
            # URL 仍然可用，路径为 null

    return result


# ============================================================
# 主流程
# ============================================================

def main():
    use_stdin = "--stdin" in sys.argv
    use_fallback = "--fallback" in sys.argv

    if use_stdin and use_fallback:
        print("混合模式：stdin + 直连fallback...", file=sys.stderr)
        current = fetch_data_hybrid()
    elif use_stdin:
        print("从 stdin 读取数据...", file=sys.stderr)
        current = fetch_data_stdin()
    else:
        print("正在获取数据（直连多数据源）...", file=sys.stderr)
        current = fetch_data_direct()

    # 检查数据是否获取成功
    has_error = False
    for name in ["us10y", "udi"]:
        if "error" in current.get(name, {}):
            has_error = True
            print(f"  [{name}] 获取失败: {current[name]['error']}", file=sys.stderr)

    if has_error:
        output = {"status": "error", "data": current, "timestamp": _now_iso()}
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)

    # 加载历史数据
    history = load_history()

    # 计算变动
    changes = calc_changes(history, current)

    # 检查预警
    alerts = check_alerts(current, changes)

    # 更新/追加今日记录
    today_rec = get_today_record(history)
    if today_rec:
        today_rec["us10y"] = current["us10y"]
        today_rec["udi"] = current["udi"]
    else:
        history["records"].append({
            "ts": _now_iso(),
            "us10y": current["us10y"],
            "udi": current["udi"]
        })

    # 保存历史
    save_history(history)

    # 生成走势图
    print("正在生成图表...", file=sys.stderr)
    charts = generate_charts(history)

    # 输出结果
    output = {
        "status": "ok",
        "timestamp": _now_iso(),
        "current": current,
        "changes": changes,
        "alerts": alerts,
        "charts": charts,
        "history_recent": [
            r["ts"][:10] + f" | US10Y: {_safe_get_value(r, 'us10y'):.3f}% | UDI: {_safe_get_value(r, 'udi'):.2f}"
            for r in history["records"][-10:]
            if _safe_get_value(r, "us10y") is not None and _safe_get_value(r, "udi") is not None
        ],
        "has_alert": len(alerts) > 0,
        "data_source": {
            "us10y": current.get("us10y", {}).get("_source", "unknown"),
            "udi": current.get("udi", {}).get("_source", "unknown")
        }
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
