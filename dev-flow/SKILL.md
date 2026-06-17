---
name: dev-flow
description: >
  Full-cycle development workflow for AI-assisted coding — plan, implement, verify, sync, ship.
  Encodes battle-tested habits: pre-work planning, surgical coding, knowledge sync, issue tracking,
  and clean Git hygiene. Trigger when starting new work, completing a phase, or when the user
  says "dev flow", "开发流程", "按流程走", "标准流程".
  NOT for trivial one-liner fixes — use judgment.
---

# Dev-Flow — 开发工作流

> Full-cycle development workflow. From idea to shipped commit. Cross-platform: Codex, Claude Code, OpenCode, OpenClaw.

## Core Philosophy

Development is not "writing code" - it is "delivering value". Writing code is only 50%. The other 50% is verification, synchronization, documentation, and shipping.

Five principles:

1. **Plan before coding** — List steps, each with a verification criterion
2. **Surgical changes only** — Touch only what you must
3. **Verify immediately** — Syntax check, import test, end-to-end run
4. **Sync immediately** — Docs must not lag behind code
5. **Ship immediately** — Don't batch commits; each step is independently traceable

---

## Standard Workflow (6 Steps)

### Step 1: Plan

Input: user request
Output: plan (3-6 verifiable steps)

- Decompose the request into verifiable steps
- Each step has a clear verification method (e.g. "syntax check passes", "import succeeds")
- Mark first step as `in_progress`
- If the request is ambiguous, ask before planning

### Step 2: Diagnose

Input: planned steps
Output: understanding of what to change and where

- **Read code first, write code second**. Never assume code structure.
- Use grep/rg to trace all hardcoded references
- If the change involves config key names, grep the entire project for residual references
- Understand the data flow: where data comes from, which layers it passes through, where it ends up

### Step 3: Implement

Input: diagnosis results
Output: modified code (passing syntax check)

- **Surgical changes only**: every changed line traces back to the user request
- **Match existing style**: even if you think there is a better way, stay consistent first
- **No speculative features**: don't build for "future needs"
- **YAML key change checklist**:
  - [ ] grep entire project for residual hardcoded references
  - [ ] Is the field available in the data source
  - [ ] Help text synchronized
  - [ ] User manual synchronized

### Step 4: Verify

Input: modified code
Output: verified code

Three verification layers: Syntax -> Import -> Functional

```python
# 1. Syntax check
python -c "import py_compile; py_compile.compile('file.py', doraise=True)"

# 2. Import check
python -c "from module import Class; print('OK')"

# 3. Functional verification (if applicable)
python tests/test_xxx.py
```

- If the project has a test suite, run related tests
- If verification fails, return to Step 3 and fix - don't skip

### Step 5: Sync

Input: verified code
Output: updated documentation

**Code changed, docs must follow.** Standard sync scope:

| Change Type | Docs to Sync |
|------------|-------------|
| New command/parameter | User manual + start.py help text |
| New feature/module | README version status + milestone docs |
| Bug fix | ISSUES.md status update |
| Config change | User manual config section + AGENTS.md |
| Architecture change | Architecture documentation |

Sync principles:
- **Don't duplicate content across files**: README for architecture, manual for commands, milestones for progress
- **Delete over retain**: outdated rule descriptions, deprecated command examples - delete them
- **AGENTS.md net growth <= 30 lines**: if more, you are stuffing in historical narrative that belongs elsewhere

### Step 6: Commit and Push (Ship)

Input: synced documentation
Output: commit on GitHub

```bash
git add <files>
git commit -m "concise description: what changed and why"
git push
```

Commit conventions:
- **Detailed commit messages**: explain what changed, why, and impact scope
- **Independent commits per step**: don't batch 10 changes into one commit
- **Push immediately after commit**: don't leave changes local
- **Network issues**: if proxy blocks GitHub, use `git -c http.proxy= push`

---

## Cross-Session Knowledge Management

### Knowledge Assets

| File | Purpose | Update Trigger |
|------|---------|---------------|
| `AGENTS.md` | AI Agent entry manual | Project structure/tech stack/constraint changes |
| `README.md` | Human-readable overview | Version upgrades/architecture changes |
| `ISSUES.md` | Issue tracking | When issues are found/fixed |
| `docs/*里程碑.md` | Phase progress | When each phase completes |

### Issue Tracking Convention (ISSUES.md)

Each issue contains:
```
### ISS-XXX: short description
- Status: done/in_progress/pending
- Priority: P0(critical)/P1(important)/P2(normal)/P3(optional)
- Description: one-sentence problem statement
- Update log: reverse chronological status changes
```

---

## Industry Best Practices Integrated

### YAGNI (You Ain't Gonna Need It)
> Don't build features for "future needs". Core constraint of Step 3.

### Boy Scout Rule
> Leave code cleaner than you found it. BUT: only clean up orphans from YOUR changes. Don't proactively refactor unrelated code.

### Single Responsibility
> One function, one thing. If a function exceeds 50 lines, consider splitting.

### Fail Fast
> Validate inputs at function entry. Invalid input returns immediately.

### Separation of Concerns
> Data fetching, business logic, presentation — three layers that don't intrude on each other.

---

## Coordination with Other Skills

| Skill | Position in Workflow |
|-------|---------------------|
| `karpathy-guidelines` | Step 3 (Implement) — constrains coding behavior |
| `neat-freak` | Step 5 (Sync) — reviews and corrects all docs |
| `dev-flow` (this file) | Entire workflow — orchestrates the above skills |

**Recommended usage**:
```
User: "build feature X"
Agent: 1) Use dev-flow to plan steps
       2) Follow karpathy-guidelines during implementation
       3) Run neat-freak after completion to sync docs
       4) Commit and push
```

---

## Anti-Patterns

- Skip planning -> start coding directly (wrong direction wastes everything)
- Skip verification -> commit only to find syntax errors
- Skip sync -> docs rot, next person hits the same pitfalls
- 10 changes in one commit -> cannot precisely locate issues
- Change YAML key names without grepping the entire project -> residual hardcoded references
- "While I'm here" refactoring of adjacent unrelated code -> introduces new bugs
