# Grok Build 配置与模型分工

这是 Grok Build 的开发工具适配，不等于 Grok 网页聊天拥有本机子 Agent 配置能力。
官方来源（2026-10-11查阅）：

- https://docs.x.ai/build/settings
- https://docs.x.ai/build/settings/reference
- https://docs.x.ai/build/features/subagents
- https://docs.x.ai/build/features/skills-plugins-marketplaces

共享规则由 AGENTS.md 承载；Grok Build 原生读取，并发现 `.grok/skills/`、
`~/.grok/skills/` 和官方兼容目录。技能本身的 frontmatter model／effort 不执行。

推荐使用 `.grok/agents/*.md` 的九个具名角色和独立 model 字段，先核对本机模板并 inspect。
用户级 `~/.grok/config.toml` 也可用 `[subagents.models]`，按内置类型设置确实可用的 ID：
`explore` 只读定位、`plan` 只读规划、`general-purpose` 生成与需要工具的工作。
项目级 `.grok/config.toml` 范围有限，不能承载完整用户模型配置。

读 `subagent-model-routing.md`；项目模式只传九角色 JSON 的 `--grok-models`。只有已选择个人作用域的三内置映射才同时传 `--grok-home`。用 `grok inspect` 验证实际加载。保留主模型、
provider、权限和已有类型模型；冲突先列差异。未执行模型任务时不声称真实型号已使用。
完整自定义角色格式来自实际安装包的官方模板／用户指南，详见模型分工指南的版本证据。
网站与本机内置类型可选性／工具范围有差异，以安装版本与实际检查为准。
