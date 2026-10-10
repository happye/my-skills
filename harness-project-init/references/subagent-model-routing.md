# 按任务能力选子 Agent 模型

适用于新项目和已有项目。只配置用户选择的工具／作用域；不重新初始化已有仓库。
主模型不改。先读该项目指令、Git 状态和现有 Agent 文件；已有授权与协作偏好优先。

## 一次配置

此 skill 自包含；整个 `harness-project-init` 目录就是可移植包。将它放到工具的
skill 目录，用「使用 harness-project-init，为当前项目配置按任务选模型」调用。
Codex：`~/.codex/skills/`；Claude Code：`~/.claude/skills/`；Grok Build：
`~/.grok/skills/`。发现目录及当前会话是否刷新以工具版本为准，也可直接读 SKILL.md。

使用已有的 Python 3.11+，不安装全局依赖。在 skill 根目录执行：

```text
python scripts/configure_subagents.py --project /path/to/project --tools codex claude
python scripts/configure_subagents.py --project /path/to/project --tools codex claude --apply
```

Windows 路径加引号，例如 `--project "G:/Tools/My Project"`；项目已有隔离 Python 时
用它代替 `python`。第一次只预览，确认具体改动符合已授权范围后执行 `--apply`；
预览不是新的用户审批门。只有缺少必要选择／授权才问用户。可只选一个工具。
`--tools portable` 只生成通用协议，不能声称已改变原生模型。

生成通用 AGENTS 指针和 `docs/agent-routing.md`；Codex／Claude 各生成六个任务角色
以及真实可发现的 Planner、Generator、Evaluator 三个角色文件。这只是配置，主控
仍要按合同调度，不能说创建了常驻服务或已经完成三 Agent 执行。

## 分工与模型选择

| 工作 | Codex 示例（当前本机已验证的组合） | Claude Code 示例 |
| --- | --- | --- |
| 定位／读代码 | Luna / high | haiku |
| 进度摘要 | Luna / low | haiku |
| 开发／普通审查 | Sol / medium | sonnet |
| 数据／费用／持久化等关键边界 | Sol / high | opus |
| 复杂架构 | Astra / low | opus |
| 普通规划／生成／独立评估 | Sol / medium | sonnet |

精确 ID 见 `assets/routing-presets.json`。这是可调整的配置示例，不是所有账号可用性
承诺或跨厂商能力等价证明。派发前核对当前工具支持的型号／推理强度；用 `--preset`
选择经过核对的 JSON，不把任何其他模型悄悄替换进去。Codex 未命名默认 Luna/medium；
Claude 未显式指定的子任务仍按自身继承规则，主控应选择已配置角色或支持的调用参数。
为兼容旧 Claude Code，安装器不写 `effort`；新版本确认支持后可按官方字段追加，
不能把 Codex 的 effort 数值直接复制到不支持它的模型。

优先直接完成简单步骤。独立委派只用于减少主上下文或必要的独立验证；不重复审查，
不高频播报；小模型不足时带证据升级一次。角色定义见项目协议模板。

## Grok Build 的真实原生分工

Grok 支持项目 `.grok/agents/*.md` 的独立 model，也支持用户级 `[subagents.models]`
类型路由。项目 `.grok/config.toml` 范围有限，不要把用户模型设置复制过去后假称生效。
前者在本机 1.0.50 安装包角色模板／用户指南和真实 inspect 中核对；见下方来源边界。

默认 `--tools grok` 仅安装项目协议。原生项目模式：从模型选择器／运行时目录核对可用 ID，
按 presets 中同样的九个角色名提供 JSON，运行：

```text
python scripts/configure_subagents.py --project /path/to/project --tools grok --grok-models /path/to/verified-nine-role-models.json --apply
```

这会生成九个项目原生角色，不改个人配置。Grok 的 effort 字段未充分核对，不编造设置；
模型选项不写未经验证的默认 ID。若仅需兼容的内置类型模型映射，JSON 改用键
`explore`、`plan`、`general-purpose`，并明确提供个人作用域：

```text
python scripts/configure_subagents.py --project /path/to/project --tools grok --grok-home /path/to/.grok --grok-models /path/to/verified-grok-models.json --apply
```

内置映射参数明确选择个人作用域，可能影响其他项目同名类型；已有不同值拒绝覆盖。
网站旧版称 plan／explore 无 shell，本机新版文档允许 explore shell 且内置类型可能不在
模型可选枚举中。因此推荐九角色项目模式并 inspect；只读配置只提供 Read／Glob／Grep，
不能执行的测试由主控供给。不要跨版本保证内置类型都可指定或工具范围相同。
Claude 兼容目录与 Grok 的 model 字段解析不要混为一谈；Grok 技能 frontmatter 的
`model`／`effort` 官方明确不执行。普通 Grok 网页聊天不能等同于 Grok Build。

## 当前会话与验证

Codex 当前会话不识别新角色时，若工具支持，用已知 default/worker + 显式型号／强度，
把角色规则写入最小任务；要求 fresh context 的运行时用 `fork_turns="none"`，
完整历史 fork 会继承主模型。新角色是否加载另开新会话验证，不泛称必须重启整个 App。
Claude 现代版本能监控已有 agents 目录，但新建目录、旧版本和某些加载方式仍需新会话；
Grok 用 inspect／Agent 管理入口确认，热刷新未经实测不保证。

验证分层：
1. 安装脚本 dry-run／apply、重复运行无改写、冲突时零写入、原配置与备份比对。
2. 用安装版本支持的配置检查／inspect 确认文件被接受、角色可发现。
3. 有授权且确有必要时，用一个小的只读任务验证委派，读取运行时实际 model／effort。
   不为凑满每个角色反复付费；派发字段是请求证据，不能代替实际执行记录。
4. 报告已配置／已加载／已执行／型号已核实的各自边界，未测试客户端明确标记。

可以以后追加其他工具，安装器合并自己生成的型号表并保留已配置选择；被人工修改的协议、同角色不同型号及不同原生文件仍拒绝覆盖。
配置冲突：先列具体 diff，与项目 owner 协调合并，不强行换掉原文件。备份位于项目
`.cache/harness-agent-routing/backups/`，`restore.json` 指向原字节；恢复前核对新 SHA，
避免覆盖安装后别人作出的变更。运行 `python scripts/test_configure_subagents.py` 做
隔离验证；不会调用任何模型或触碰真实个人配置。

## 信源与边界（2026-10-11 查阅）

- [OpenAI：Subagents](https://developers.openai.com/codex/subagents)：独立 TOML、原生字段、继承、默认模型、权限覆盖及 token 成本。
- [OpenAI：Config reference](https://developers.openai.com/codex/config-reference)：`config.toml`、受信任项目配置及 `[agents]`。
- [Claude Code：Custom subagents](https://code.claude.com/docs/en/sub-agents)：Markdown frontmatter、模型别名、工具限制、版本相关刷新与 `/tasks`。
- [Grok Build：Settings reference](https://docs.x.ai/build/settings/reference)：`[subagents.models]`。
- [Grok Build：Settings](https://docs.x.ai/build/settings)：用户／项目作用域限制与 `grok inspect`。
- [Grok Build：Subagents](https://docs.x.ai/build/features/subagents)：内置类型与能力。
- [Grok Build：Skills](https://docs.x.ai/build/features/skills-plugins-marketplaces)：发现目录、兼容与技能 model 字段不执行。
- [Anthropic：Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)：三角色、合同与按模型能力裁剪；这是工程实验，不是所有项目必须三 Agent 的官方强制规范。

来源证明配置机制；账号权限和本机执行由实际验证证明。配置文件本身不能证明节省了多少
额度；比较同任务输入、输出和质量后才能报告实测节省，不能编造固定比例。

### Grok 本机一手证据

当前安装包 1.0.50（c58f321264ba）的 `docs/user-guide/16-subagents.md` 与
`bundled/agents/general-purpose.md`／`explore.md` 提供 Markdown frontmatter、model、
prompt_mode、permission_mode、agents_md 模板及模型 pin 顺序；它比网页简版更详细。
安装器采用这些字段，并在隔离项目用实际 `grok --no-auto-update inspect --json` 核对发现。
这证明当前安装版本接受／发现文件，不能代替真实执行或证明每个账号能调用该 ID。
其他安装版本缺少同格式／验证入口时退回通用协议，注明限制，不虚构兼容。
