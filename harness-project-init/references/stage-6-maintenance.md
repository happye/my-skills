# Stage 6: 持续维护

## 目标
控制系统熵增，持续偿还技术债务，保持文档时效性。

## 操作清单

### 6.1 Doc-Gardening Agent

定期运行后台 Agent 扫描过时文档：

```markdown
你是 Doc-Gardening Agent。执行以下检查:

1. 扫描 docs/ 下所有文档
2. 检查交叉链接是否有效
3. 检查文档中引用的文件路径是否存在
4. 检查文档最后修改日期，超过 30 天的标记为"可能过时"
5. 检查 AGENTS.md 中的引用是否指向存在的文档
6. 发现问题时开修复 PR

输出: docs/exec-plans/doc-gardening-[日期].md
```

建议频率：每周一次（可通过 cron 自动触发）。

### 6.2 质量评分 Agent

定期扫描代码偏差：

```markdown
你是 Quality Audit Agent。执行以下检查:

1. 扫描最近 7 天的 git commit
2. 检查是否有不符合编码规范的代码
3. 检查是否有文件超过 300 行限制
4. 检查是否有函数圈复杂度超过 10
5. 检查是否有被 Agent 复制的不好的模式
6. 更新质量评分

输出: docs/exec-plans/quality-audit-[日期].md
```

### 6.3 黄金原则

在 `docs/references/golden-principles.md` 中记录项目黄金原则：

```markdown
# 黄金原则

1. 永远不要在 UI 层直接访问数据库
2. 所有外部 API 调用必须有超时和重试
3. 所有用户输入必须经过校验和清理
4. 错误信息必须对用户友好，不暴露技术细节
5. 新功能必须有对应的测试
6. 公共 API 必须有文档
```

### 6.4 技术债务处理

技术债务像高息贷款：持续小额偿还优于累积后爆发式处理。

- 发现 debt 时立即在 `docs/exec-plans/tech-debt.md` 记录
- 每周分配一个 sprint 专门处理 debt
- debt 记录格式：

```markdown
## DEBT-001: [描述]
- 发现日期: [日期]
- 严重程度: low/medium/high
- 影响: [描述]
- 计划偿还: [日期]
```

## 关键原则

- **Agent 会复制坏模式**：定期扫描纠偏
- **技术债务持续偿还**：不要累积
- **文档有时效性**：doc-gardening 保持文档新鲜
- **黄金原则编码到仓库**：让 Agent 在约束内工作
