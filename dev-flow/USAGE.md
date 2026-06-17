# Dev-Flow 使用场景说明

> 本文档通过典型案例，帮助 AI Agent 判断何时触发 `dev-flow` 技能，以及在不同场景下如何调整工作流。

## 触发判断

| 场景 | 是否触发 dev-flow | 说明 |
|------|:--:|------|
| 新增功能模块（如"加一个回测框架"） | ✅ 触发 | 完整六步流程 |
| 修改多个文件的重构（如"把数据源从 AKShare 换成 Baostock"） | ✅ 触发 | 重点在 Step 2 诊断和 Step 4 验证 |
| 修复一个边界明确的 Bug | ✅ 触发 | 走精简版：诊断→修复→验证→同步 ISSUES |
| 改一行配置值（如"把超时从 10 改成 15"） | ❌ 跳过 | 直接改，验证语法即可 |
| 问一个关于代码的问题（如"这个函数是干什么的"） | ❌ 跳过 | 纯信息查询，无代码变更 |
| 用户明确说"按流程走"、"标准流程"、"开发流程" | ✅ 强制触发 | 用户显式指令 |

## 典型场景示例

### 场景 1：新增功能模块

**用户**："给扫描器加一个行业过滤功能"

**Agent 行为**：
1. **Plan**：列出步骤 — ① 研究现有 scanner_engine 结构 ② 新增 filter 逻辑 ③ 修改 CLI 参数 ④ 更新帮助文本 ⑤ 同步文档
2. **Diagnose**：`rg "scanner_engine"` 找入口，读 market_cache.py 了解数据流
3. **Implement**：只改扫描相关文件，不碰数据源层
4. **Verify**：`python -c "from src.scanner import ..."` → `python -m src.cli.main -h` 确认帮助文本
5. **Sync**：使用手册加"行业过滤"章节，README 版本说明
6. **Ship**：`git commit -m "feat: 扫描器新增行业过滤功能"`

### 场景 2：修改 YAML 配置键名

**用户**："把 scan_rules.yaml 里的 `default` 规则改名为 `healthy_pullback`"

**Agent 行为**：
1. **Plan**：改名 + 全局 grep + 同步文档
2. **Diagnose**：`rg "default" --type yaml` + `rg '"default"' --type py` 全项目搜索
3. **Implement**：改 YAML + 改 8 处硬编码 + 改帮助文本
4. **Verify**：`python -m src.cli.main -h` 确认规则名已更新
5. **Sync**：手动更新"默认规则"所有引用
6. **Ship**：一次 commit 包含所有 8 处修改

### 场景 3：多数据源 Bug 修复

**用户**："扫描持仓时报错 `expected str, not dict`"

**Agent 行为**：
1. **Plan**：复现 → 定位 → 修复 → 验证
2. **Diagnose**：追踪数据流：`s 命令 → to_strategy_state → 某个字段期望 str 但拿到 dict`。读 `portfolio.py` 和 `orchestrator.py` 中的类型转换逻辑。
3. **Implement**：在数据入口处加类型转换/防御
4. **Verify**：`python start.py` → 输入 `s` 确认不再报错
5. **Sync**：ISSUES.md 标记对应 ISS 为已解决
6. **Ship**：`git commit -m "fix: 持仓扫描 dict 类型错误"`

### 场景 4：阶段开发收尾

**用户**："这个阶段做完了，新人能直接上手"

**Agent 行为**：
1. dev-flow Step 5（Sync）升级为完整 neat-freak 审计
2. 逐文件审查：AGENTS.md、README、使用手册、里程碑、ISSUES
3. 删除过时描述、合并重复内容、修正版本号
4. 输出变更摘要
5. Ship：标记里程碑完成 + `git tag v0.x.y`

## 与其他 Skill 的配合

| 场景 | dev-flow | karpathy-guidelines | neat-freak |
|------|:--:|:--:|:--:|
| 日常功能开发 | 全程编排 | Step 3 约束编码 | Step 5 同步 |
| 单文件小修改 | 走精简版 | 约束"不顺手重构" | 检查帮助文本 |
| 阶段收尾 | Step 5 升级 | — | 完整审计 |
| 代码审查 | — | 对照反模式表审查 | 对照文档一致性 |

## 快速决策树

```
收到开发请求
  │
  ├─ 纯信息查询？ → 不触发，直接回答
  ├─ 改一行配置？ → 不触发，直接改 + 验证
  ├─ 用户说"按流程"？ → 强制触发完整六步
  ├─ 单文件 Bug 修复？ → 触发精简版（诊断→修复→验证→同步→提交）
  └─ 多文件功能开发？ → 触发完整六步
```
