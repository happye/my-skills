# 模型分工扩展的验证记录

2026-10-11，在远端 v2.0 基础上增量修改；保留原有 Stage 7 记忆资产、Stage 8 工程门禁和其他工具模板。新增配置模式与三角色实际配置，不把生成文档当作已运行 Agent。

## 已验证

- Python 3.13／Windows 的隔离测试共 13 项：12 通过，1 项因系统未允许创建测试符号链接跳过。覆盖 dry-run、重复安装字节一致、冲突零写入、BOM／CRLF、追加工具、保留父模型及新／旧并发上限、原字节备份、并发改动／删除保护、写入失败回滚、Grok 项目与个人作用域分离。
- Skill frontmatter 验证和新增 Python 格式／lint 通过。脚本仅需标准库，最低 Python 3.11；其他系统／版本仍应运行随包测试，不能把当前 Windows 结果说成全平台实测。
- Codex 0.162.0-alpha.17.2：隔离 HOME／受信任项目的 app-server strict-config 与 config/read 接受默认配置，父模型保持。未信任项目配置不会加载，验证时只在隔离 HOME 注册信任；未改真实全局信任或权限。
- Grok Build 1.0.50（c58f321264ba）：隔离项目真实 inspect 发现九个 `.grok/agents/*.md` 角色，包括 Planner／Generator／Evaluator；未发推理请求、未更改真实个人模型设置。项目仍未授权执行，发现与运行是不同状态。
- Claude Code 2.1.177：采用可兼容的 name／description／tools／model frontmatter，未使用新版 effort／watcher 特性。静态检查通过；本轮未委派 Claude 模型，不能声称已执行。
- 独立审查识别并修正了保留旧并发 cap、追加第二工具、CRLF 兼容、并发删除回滚、只读角色报告持久化归属问题。最后核对无新增发现。

## 证据边界

本轮配置检查不发模型请求。此前同一 Codex 环境的 Luna/high、Sol/medium、Astra/low 已通过实际子任务和运行时 model／effort 元数据验证；本轮亦用 Luna/high 做只读历史定位、Sol/medium 做独立审查。不能把这些任务当作新九角色全部已执行，也不据此声称 Claude／Grok 调用成功。

跨工具的通用部分是分工、边界、合同、交接与实际证据；各厂商字段／模型 ID 由其原生适配处理。不同账号、provider、版本或受管策略可能改变可用性。现有聊天支持明确派发型号时可立即使用；新命名角色及新 skill 的发现按客户端实际检查决定，不保证所有工具热加载。

Grok 网页简版与当前安装包存在差异：网页描述内置 explore 无 shell，本机 user-guide 与 bundled 模板允许只读 shell，且内置类型可能不在模型可选枚举。采用安装版本的一手模板并 inspect，默认具名只读角色不授予 shell；不沿用网页简版作全版本承诺。来源路径和机制见 `subagent-model-routing.md`。
