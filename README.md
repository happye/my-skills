# My Skills

Personal collection of AI Agent skills. Each skill is self-contained and dependency-free.

## Skills

| Skill | Description |
|-------|-------------|
| `dev-flow` | Universal development workflow: plan, diagnose, implement, verify, sync, ship. Self-contained, zero dependencies, works on any project. Integrates YAGNI, Rule of Three, TDD Bug Fixing, Graceful Degradation, SemVer. |

## Installation

Copy any skill directory to your agent's skills directory.

```bash
# Codex
cp -r dev-flow ~/.codex/skills/

# Claude Code
cp -r dev-flow ~/.claude/skills/
```

Each skill works independently. No cross-skill dependencies.

## Usage

The skill auto-triggers on "dev flow", "开发流程", or when starting new work.

```
User: "add export feature"
Agent: Plan → Diagnose → Implement → Verify → Sync → Ship
```
