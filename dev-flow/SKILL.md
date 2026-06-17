---
name: dev-flow
description: >
  Full-cycle development workflow for AI-assisted coding. Plan, diagnose, implement,
  verify, sync, ship. Encodes battle-tested habits: pre-work planning, surgical coding,
  knowledge sync, issue tracking, clean Git hygiene. Integrates industry patterns:
  YAGNI, Rule of Three, Test-Driven Bug Fixing, Graceful Degradation, SemVer,
  Configuration-Driven Development, Network-Aware Coding.
  Trigger when: starting new work, completing a phase, "dev flow", "按流程走", "标准流程".
  NOT for trivial one-liner fixes.
---

# Dev-Flow — AI-Assisted Development Workflow

> Full-cycle workflow. From idea to shipped commit. Cross-platform.

## Core Philosophy

Development is not "writing code" — it is "delivering value". Code is 50%.
The other 50%: verification, sync, docs, shipping.

Five principles:

1. **Plan before coding** — Verifiable steps before any code
2. **Surgical changes only** — Every line traces to the request
3. **Verify immediately** — Syntax → Import → Functional, in order
4. **Sync immediately** — Docs follow code; never lag behind
5. **Ship immediately** — Atomic commits, push right after

---

## Standard Workflow (6 Steps)

```
Plan → Diagnose → Implement → Verify → Sync → Ship
  ^                                              |
  +————— if verify fails ———————————————————————+
```

### Step 1: Plan

Input: user request
Output: plan (3-6 verifiable steps)

- Decompose request into verifiable steps; each with a verification criterion
- Mark first step `in_progress`; keep exactly one active
- If ambiguous, ask before planning — don't guess

### Step 2: Diagnose

Input: planned steps
Output: understanding what to change, where, and why

- **Read code first, write code second**. Never assume structure.
- `rg` to trace all hardcoded references (especially config key names)
- Map data flow: source → layers → destination. Know which fields each layer consumes.
- **For bugs**: reproduce first, then fix. Unreproducible = unverifiable.

### Step 3: Implement

Input: diagnosis results
Output: modified code (syntax-clean)

- **Surgical**: every changed line traces to the request
- **Style-consistent**: match existing patterns, even if you'd do it differently
- **No speculation**: don't build for unrequested future needs

**Config/YAML change checklist:**
- [ ] `rg "old_key"` across entire project before rename
- [ ] Field available in all active data sources
- [ ] CLI help text updated
- [ ] User manual updated

### Step 4: Verify

Input: modified code
Output: verified code

Three layers, must pass each before proceeding:

```python
# L1: Syntax
python -c "import py_compile; py_compile.compile('file.py', doraise=True)"

# L2: Import
python -c "from module import Class; print('OK')"

# L3: Functional
python tests/test_xxx.py
```

- **For bugs**: write failing test BEFORE fixing, then verify it passes
- If any layer fails, return to Step 3 — don't skip

### Step 5: Sync

Input: verified code
Output: updated documentation

| Change Type | Docs to Sync |
|------------|-------------|
| New command/parameter | Manual + help text |
| New feature/module | README + milestone docs |
| Bug fix | ISSUES.md |
| Config change | Manual + AGENTS.md |
| Architecture change | Architecture docs |

**Sync principles:**
- **No duplication**: README=architecture, manual=commands, milestones=progress
- **Delete > retain**: outdated descriptions, deprecated examples — delete them
- **AGENTS.md net growth ≤ 30 lines**: if more, you're writing changelog, not manual

### Step 6: Ship (Commit & Push)

Input: synced docs
Output: commit on GitHub

```bash
git add <files>
git commit -m "type: what changed, why, impact scope"
git push
```

**Commit discipline:**
- **Atomic**: one logical change per commit
- **Descriptive**: explain what, why, impact — never "fix bugs"
- **Push immediately**: never batch commits locally
- **Tag releases**: `git tag v0.x.y` after milestone completion

---

## Industry Best Practices

### YAGNI (You Ain't Gonna Need It)
Don't build for unrequested future needs. Every line has maintenance cost.
Speculative code is negative value.

### Boy Scout Rule
Leave code cleaner than you found it. BUT: only clean orphans from YOUR changes.
Never refactor unrelated code "while you're here".

### Single Responsibility
One function, one thing. If >50 lines, consider splitting.
If you need "and" to describe a function, it does too much.

### Fail Fast
Validate at function entry. Bad data returns immediately with a clear message.
Don't let errors propagate through layers.

### Separation of Concerns
Data fetching → Business logic → Presentation. Three layers, no intrusion.
Changing UI must not require changing DB layer.

### The Rule of Three
- 1st time: write it
- 2nd time: copy with `# TODO: extract`
- 3rd time: refactor into shared utility

Premature abstraction > duplication. Wait for the pattern to prove itself.

### Test-Driven Bug Fixing
1. Write failing test that reproduces the bug
2. Apply the fix
3. Verify test passes
4. Commit test + fix together

### Semantic Versioning
`vMAJOR.MINOR.PATCH` — MAJOR: breaking, MINOR: new feature (compatible), PATCH: bug fix.

---

## Battle-Tested Patterns

### Configuration-Driven Development

Config key names are API contracts. Treat renaming as breaking changes.

**Before renaming a config key:**
- [ ] `rg "old_key"` across entire project (Python + YAML + docs + tests)
- [ ] Check test fixtures and expected outputs
- [ ] Check CLI help text and manuals

**After renaming:**
- [ ] Full test suite
- [ ] Manual test of affected CLI commands
- [ ] Update ISSUES.md if the change fixes a bug

### Graceful Degradation (Multi-Source Data)

```
Primary → Fallback1 → Fallback2 → Soft Failure
```

- Each fallback needs a clear trigger (timeout, error code, missing field)
- Never silently return partial data — log WARNING at minimum
- Missing optional fields → skip dependent filters, don't crash
- Network errors → exponential backoff (1s, 2s, 4s) then degrade
- Document: which fields each source provides, which are missing

**Anti-pattern**: `except Exception: return {}` — masks real bugs.

### Script Lifecycle

Temporary scripts:
- Prefix: `_xxx.py` (underscore = disposable)
- Delete after use, never commit
- If permanent, move to `tests/test_xxx.py`, remove underscore

Permanent scripts:
- Must work after fresh clone
- Dependencies installable via documented method
- Environmental assumptions documented in AGENTS.md

### Network-Aware Coding

- **Proxy bypass**: financial APIs often fail through corporate proxies
- **Git + proxy**: `git -c http.proxy= -c https.proxy= push` when blocked
- **Timeout everything**: default 15s, critical paths 5s
- **Retry with backoff**: 1-3 retries for transient failures

### Issue Tracking Discipline

```
### ISS-XXX: short description
- Status: done | in_progress | pending
- Priority: P0(critical) | P1(important) | P2(normal) | P3(optional)
- Description: one sentence
- Direction: feature area / milestone phase
- Dependencies: ISS-xxx, ISS-yyy
- Update log: reverse chronological, with dates
```

**Rules:**
- Every bug found gets ISS number BEFORE fixing
- Mark resolved after verification, not after coding
- P0 blocks milestone; P3 accumulates for cleanup sprints

### Terminal/CLI Hygiene

- **Help text must be exhaustive**: all commands, parameters, rules in `-h`
- **Error messages must be actionable**: "API timeout (15s): check proxy 127.0.0.1:7890"
- **Progress for >3s ops**: spinner or counter
- **Exit codes**: 0=success, non-zero=failure — for automation

---

## Knowledge Management

### The AGENTS.md Contract

First file any AI agent reads. Must contain:

| Section | Content |
|---------|---------|
| How to Run | Exact install + start commands |
| What This Is | Architecture summary (3-5 bullets) |
| Project Structure | Key directories + purposes |
| Tech Stack | Layer → technology table |
| Key Constraints | Pitfalls, gotchas, source quirks, network issues |
| Current State | Done + P0/P1 pending |
| Document Index | All docs with content descriptions |

**Maintenance**: net growth ≤ 30 lines/update. Move narratives to git history or CHANGES.md.

### Document Separation

| Document | Audience | Scope |
|----------|----------|-------|
| AGENTS.md | AI agents | Rules, constraints, quick start |
| README.md | Humans | Overview, architecture, version history |
| User Manual | End users | Commands, workflows, FAQ |
| Architecture Docs | Developers | Modules, data flow, API |
| Milestone Docs | PM/Team | Progress, deliverables, criteria |
| ISSUES.md | Team | Bugs, debt, enhancements |
| CHANGES.md | Everyone | Chronological version log |

### Knowledge Decay Prevention

After every session, check:
- [ ] All manual commands still work?
- [ ] Config keys in docs still valid?
- [ ] AGENTS.md constraints reflect latest pitfalls?
- [ ] README version matches latest tag?
- [ ] No relative time references ("recently", "last week")?

---

## Skill Coordination

| Skill | Stage | Role |
|-------|-------|------|
| `karpathy-guidelines` | Step 3 | Constrain coding: simplicity, surgical, goal-driven |
| `neat-freak` | Step 5 | OCD-level doc reconciliation |
| `dev-flow` | All | Orchestrator |

**Pattern:**
```
User: "build X"
→ dev-flow: plan steps
→ karpathy-guidelines: constrain implementation
→ neat-freak: sync all docs
→ ship: commit + push
```

---

## Anti-Patterns Catalog

| Anti-Pattern | Damage | Fix |
|-------------|--------|-----|
| Skip plan, code directly | Wrong direction wastes everything | 3-6 verifiable steps first |
| Skip verification | Syntax errors at commit | Syntax check after every file |
| Skip sync | Docs rot, next agent hits pitfalls | Sync in same commit |
| 10 changes in 1 commit | Can't bisect breakage | One logical change per commit |
| Rename YAML key without grep | 8+ residual hardcoded refs | `rg "old_key"` before rename |
| "While I'm here" refactor | Unrelated bugs introduced | Open ISSUE; stay surgical |
| `except Exception: pass` | Masks real bugs | Catch specific; log WARNING |
| Hardcode config values | Change = redeploy, not reconfigure | Extract to config file |
| Copy-paste 4+ times | Fix in 1 place, 3 copies broken | Extract on 3rd duplication |
| Commit "fix bugs" | Useless for history | "Fix: preclose type error in Baostock weekly" |
| Chinese full-width in code | SyntaxError on Windows | ASCII punctuation only |
| Push through proxy | Connection reset silently | `git -c http.proxy= push` |

---

## Quick Reference

```
Plan → Diagnose → Implement → Verify → Sync → Ship
  ^                                              |
  +————— if verify fails ———————————————————————+

Config change:  rg old → change → grep → sync → commit
Bug fix:        repro → test → fix → verify → ISSUES → commit
New feature:    plan → diagnose → code → syntax → functional → docs → commit
```
