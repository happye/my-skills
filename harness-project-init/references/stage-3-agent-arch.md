# Stage 3: Agent 架构

## 目标
建立 Planner → Generator → Evaluator 三 Agent 体系，基于 GAN 思想实现自进化。

## 三 Agent 角色定义

### Planner Agent（规划者）

**职责**：将简单 prompt 扩展为完整产品规格

```
输入: 1-4 句话的用户需求
输出: docs/product-specs/spec.md（完整产品规格）

规则:
- 对范围有野心
- 关注产品上下文和高层技术设计，而非详细技术实现
- 主动寻找 AI 功能融入产品的机会
- 输出写入 docs/product-specs/spec.md
```

**Planner Prompt 模板**：

```markdown
你是 Planner Agent。接收以下需求，扩展为完整产品规格。

需求: [用户输入]

要求:
1. 扩展为完整产品规格，写入 docs/product-specs/spec.md
2. 对范围有野心，不要保守
3. 定义 200+ 个具体特性
4. 每个特性包含: id, name, description, priority, test_criteria
5. 将特性列表输出为 feature_list.json（JSON 格式）
6. 关注产品上下文，不需要写详细技术实现
```

### Generator Agent（生成者）

**职责**：按 sprint 工作，每次从 spec 中取一个特性实现

```
输入: feature_list.json + progress.md
输出: 代码变更 + git commit + progress 更新

规则:
- 每个 sprint 只做一个特性
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
5. 运行 ./scripts/init.sh 启动开发服务器
6. 实现该特性
7. 用浏览器自动化做基本端到端测试
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

硬阈值: 每个维度 ≥ 7 才算通过
```

**Evaluator Prompt 模板**：

```markdown
你是 Evaluator Agent。对 Generator 的最新 sprint 进行评估。

评估流程:
1. 读 feature_list.json 确认当前 sprint 的特性
2. 读 sprint 合同确认"完成"标准
3. 使用 Playwright MCP 操作运行中的应用:
   - 测试 UI 功能
   - 测试 API 端点
   - 检查数据库状态
4. 按以下维度评分 (0-10):
   - 产品深度: 功能是否完整、有深度
   - 功能性: 是否能正常工作
   - 视觉设计: 是否有独特设计、一致视觉语言
   - 代码质量: 代码结构、命名、错误处理
5. 每个维度硬阈值 ≥ 7
6. 如果任何维度 < 7，给出详细反馈写入 docs/exec-plans/feedback-[sprint-id].md
7. 如果全部 ≥ 7，标记 sprint 通过
```

## Sprint 合同机制

每个 sprint 前，Generator 和 Evaluator 通过文件通信协商：

```
1. Generator 写 docs/exec-plans/sprint-[id]-proposal.md
   - 本 sprint 要建造什么
   - 如何验证
2. Evaluator 读后写 docs/exec-plans/sprint-[id]-review.md
   - 审查是否建造正确的东西
   - 补充验证标准
3. 双方迭代直到达成一致
4. 合同锁定，Generator 开始工作
```

## Agent 间通信协议

- **通过文件通信**：一个 Agent 写文件，另一个读并回复
- **不直接对话**：避免上下文污染
- **所有协商记录在 docs/exec-plans/**：可追溯

## 关键原则

- **GAN 思想**：Generator 和 Evaluator 对抗提升
- **文件通信**：Agent 间不直接对话，通过文件交换信息
- **Sprint 合同**：就"完成"标准达成一致后再开工
- **一次一个特性**：避免上下文耗尽
