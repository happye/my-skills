# My Skills

Personal collection of AI Agent skills for coding workflow.

## Skills

| Skill | Description | Version |
|-------|-------------|---------|
| `dev-flow` | Full-cycle development workflow: plan, diagnose, implement, verify, sync, ship. Integrates YAGNI, Rule of Three, Test-Driven Bug Fixing, Graceful Degradation, SemVer, Configuration-Driven Development, and more. | v1.1 |

## What's in dev-flow

The `dev-flow` skill encodes battle-tested development patterns into a repeatable 6-step workflow:

```
Plan → Diagnose → Implement → Verify → Sync → Ship
```

### Integrated Best Practices

| Practice | Source | How It's Applied |
|----------|--------|-----------------|
| YAGNI | Extreme Programming | No speculative features; code only what's asked |
| Rule of Three | Martin Fowler | Extract on 3rd duplication, not before |
| Test-Driven Bug Fixing | Pragmatic Programmer | Reproduce bug in test before fixing |
| Graceful Degradation | Distributed Systems | Multi-source fallback chain with clear triggers |
| Configuration-Driven Dev | 12-Factor App | Config keys are API contracts — treat renames as breaking |
| Boy Scout Rule | Clean Code | Leave it cleaner, but YOUR changes only |
| Fail Fast | Pragmatic Programmer | Validate at function entry, return immediately on bad input |
| Separation of Concerns | Software Architecture | Data → Logic → Presentation, three independent layers |
| Semantic Versioning | semver.org | vMAJOR.MINOR.PATCH discipline |
| Network-Aware Coding | Real Project Learning | Proxy bypass, timeouts, exponential backoff |
| Script Lifecycle | Real Project Learning | `_xxx.py` = disposable; permanent scripts must work from clone |
| Knowledge Decay Prevention | Real Project Learning | After every session: verify docs, config keys, versions still match |

### What It Prevents

The skill catalogs 12 concrete anti-patterns with damage assessment and fixes, including:
- Renaming YAML keys without `rg` grep → residual hardcoded refs in 8+ files
- `except Exception: pass` → masks real bugs silently
- Chinese full-width punctuation in Python → SyntaxError on Windows
- "While I'm here" refactoring → unrelated new bugs
- 10 changes in one commit → can't bisect breakage

## Installation

Copy the skill directory to your agent's skills directory.

### Codex
```bash
cp -r dev-flow ~/.codex/skills/
```

### Claude Code
```bash
cp -r dev-flow ~/.claude/skills/
```

### OpenClaw
```bash
cp -r dev-flow ~/.openclaw/skills/
```

## Usage

The skill auto-triggers when you say "dev flow", "按流程走", or when starting new development work. It coordinates with `karpathy-guidelines` (coding constraints) and `neat-freak` (doc sync).

```
User: "build feature X"
Agent: 1) dev-flow: plan steps
       2) karpathy-guidelines: constrain implementation
       3) neat-freak: sync all docs
       4) ship: commit + push
```

## Changelog

### v1.1 (2026-06-18)
- Added 12 industry best practices with concrete application guidance
- Added Battle-Tested Patterns section (Config-Driven Dev, Graceful Degradation, Script Lifecycle, Network-Aware Coding, Issue Tracking, CLI Hygiene)
- Added Knowledge Management section (AGENTS.md Contract, Document Separation, Decay Prevention)
- Expanded Anti-Patterns from 5 to 12 with damage/fix columns
- Added Quick Reference Card
- Added Skill Coordination table

### v1.0 (initial)
- 6-step workflow: Plan → Diagnose → Implement → Verify → Sync → Ship
- Basic best practices: YAGNI, Boy Scout Rule, Single Responsibility, Fail Fast
- 5 anti-patterns
