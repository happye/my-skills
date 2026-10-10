# Stage 3: Agent 架构

## 目标
建立 Planner → Generator → Evaluator 的开发协作流程，并按支持能力落地为真实可发现的 Agent。对抗评估是职责分离的启发，不是 GAN 训练或自动自进化保证。

## 三 Agent 角色定义

### Planner Agent（规划者）

**职责**：在已批准范围内形成规格或本轮合同；只读 Planner 返回草案，由集成负责人持久化

```
输入: 1-4 句话的用户需求
输出: docs/product-specs/spec.md（完整产品规格）

规则:
- 在已批准的范围内完善用户场景与可测标准
- 关注产品上下文和高层技术设计，而非详细技术实现
- 主动寻找 AI 功能融入产品的机会
- 返回输出；由集成负责人写入 docs/product-specs/spec.md
```

**Planner Prompt 模板**：

```markdown
你是 Planner Agent。接收以下需求，扩展为完整产品规格。

需求: [用户输入]

要求:
1. 返回规格／合同草案及目标路径；由集成负责人写入已有规格或 docs/product-specs/spec.md
2. 尊重已有规格、阶段门槛和用户优先级，不扩展已冻结范围
3. 按实际需求列出有界特性；已有 feature_list.json 时增量维护，禁止固定 200+ 配额
4. 每个特性包含: id, name, description, priority, test_criteria
5. 返回特性列表 JSON 草案，由集成负责人合并 feature_list.json；只读角色不直接写文件
6. 关注产品上下文，不需要写详细技术实现
```

### Generator Agent（生成者）

**职责**：按 sprint 工作，每次从 spec 中取一个特性实现

```
输入: feature_list.json + progress.md
输出: 代码变更 + git commit + progress 更新

规则:
- 每个 sprint 聚焦一个有界交付，完成后可以按路径继续
- sprint 开始前与 Evaluator 协商"完成"标准
- 使用 git 进行版本控制
- sprint 结束时自我评估
```

**Generator Prompt 模板**：

```markdown
你是 Generator Agent。执行以下流程:

1. pwd 确认工作目录
2. 读 git log --oneline -10 了解最近工作
3. 读 progress.md 了解当前状态
4. 读 feature_list.json，选择最高优先级的 passes: false 特性
5. 运行项目真实的环境／启动检查（Windows 可为 init.ps1；CLI 项目不必启动 Web 服务）
6. 实现该特性
7. 运行符合项目类型的行为验证；有 UI 时使用可用浏览器工具，CLI／库使用实际命令或测试
8. git commit 并写描述性提交信息
9. 更新 progress.md
10. 仅在测试通过后才将特性标记为 passes: true
```

### Evaluator Agent（评估者）

**职责**：用浏览器自动化测试运行中的应用，按维度评分

```
输入: Generator 的 sprint 产出
输出: 评估报告 + 评分 + 反馈

评估维度:
1. 产品深度 (Product Depth): 0-10
2. 功能性 (Functionality): 0-10
3. 视觉设计 (Visual Design): 0-10
4. 代码质量 (Code Quality): 0-10

默认参考阈值: 适用维度 ≥ 7；项目正式验收指标优先，不用评分代替真实测试或人工判断
```

**Evaluator Prompt 模板**：

```markdown
你是 Evaluator Agent。对 Generator 的最新 sprint 进行评估。

评估流程:
1. 读 feature_list.json 确认当前 sprint 的特性
2. 读 sprint 合同确认"完成"标准
3. 按项目类型和实际可用工具验证，Web 可使用 Playwright MCP:
   - 测试 UI 功能
   - 测试 API 端点
   - 检查数据库状态
4. 按以下维度评分 (0-10):
   - 产品深度: 功能是否完整、有深度
   - 功能性: 是否能正常工作
   - 视觉设计: 是否有独特设计、一致视觉语言
   - 代码质量: 代码结构、命名、错误处理
5. 对适用维度采用合同约定阈值；不适用项记 N/A，缺失证据记 unverified
6. 如果未达到合同标准，给出复现和影响，由集成负责人将反馈写入 docs/exec-plans/feedback-[sprint-id].md
7. 只有合同验收与必要人工判定都完成才通过；不能用自评分覆盖正式质量门
```

## Sprint 合同机制

每个 sprint 前，Generator 和 Evaluator 通过文件通信协商：

```
1. Generator 写 docs/exec-plans/sprint-[id]-proposal.md
   - 本 sprint 要建造什么
   - 如何验证
2. 只读 Evaluator 返回评审，由集成负责人写 docs/exec-plans/sprint-[id]-review.md
   - 审查是否建造正确的东西
   - 补充验证标准
3. 一次有证据的评审后锁定标准；关键缺口阻断依赖任务，小问题记录债务，不无限协商
4. 合同锁定，Generator 开始工作
```

## Agent 间通信协议

- **通过文件留痕**：Generator 写其 owner 文件；只读 Planner／Evaluator 返回内容，由集成负责人写入对应合同／评审文件
- **工具消息用于协调**：有支持时可传短摘要；正式标准与结论仍落文件，不复制全部历史
- **所有协商记录在 docs/exec-plans/**：可追溯

## 关键原则

- **独立评估**：职责分离帮助发现缺陷，不承诺自动训练或固定质量提升
- **文件留痕**：用文件保存合同、判断与证据，支持的工具消息负责短协调
- **Sprint 合同**：就"完成"标准达成一致后再开工
- **一次一个特性**：避免上下文耗尽

## 原生角色配置与启动验收（必做）

角色说明文件不等于三个运行中的 Agent。读 `subagent-model-routing.md`，用自包含安装器增量生成：

- Codex：`.codex/agents/harness_{planner,generator,evaluator}.toml`（各自 name 是角色标识），并合并 `.codex/config.toml` 的原生默认项。
- Claude Code：`.claude/agents/harness_{planner,generator,evaluator}.md`，按该工具原生 model 别名／ID 选择型号。
- Grok Build：使用已核实的九角色→型号 JSON 生成项目 `.grok/agents/*.md`，含真实 Planner／Generator／Evaluator；用户级 `[subagents.models]` 的三内置类型映射是可选兼容模式。内置类型是否可选及工具范围随版本变化，先用 inspect／运行时确认。
- 其他工具：生成通用合同与任务说明；不支持原生派发／型号控制时明确单 Agent 顺序执行或未配置，不能称独立评估已完成。

项目初始化时产出一条状态记录：工具版本、配置路径、可用模型、角色发现结果、实际执行 task ID／真实型号（未测为 unknown）、合同路径、降级原因和下一步。原生配置静态通过不能代替委派成功。只有实际完成的独立任务才能称多 Agent 已运行。

主控负责依赖调度和合入，不建立未经请求的后台循环。规划通常由主控或 balanced Planner 完成；复杂设计才派 Architect；实现完成后派一个独立 Evaluator，关键边界升级该评估角色，避免重复 reviewers。简单改动由主控直接处理并记为单 Agent。三个阶段按先后执行，不强制三个模型同时运行。

既有项目迁移：先保留规格、记忆、门禁和已验证角色；使用现有 task_developer／task_reviewer 承载 Generator／Evaluator 也可，但记录实际 owner 和执行模式。不要为了形式再创建重复角色或重跑所有业务测试。
