# Project agent routing and milestone workflow

This is a collaboration contract, not a background scheduler. Project/user scope,
permissions, budget and phase gates remain authoritative. Models below are requests;
availability, registry discovery and completed execution need separate evidence.

## Capability routing

- Exploration: the smallest capable model, enough reasoning to trace relevant code.
- Progress: inexpensive model, short changed-state summary; no periodic unchanged polling.
- Implementation and ordinary review: balanced coding model.
- Data, fees, persistence, concurrency and identity review: stronger reasoning or model.
- Complex architecture: strongest available design model only when complexity warrants it.
- Simple work: handle directly. Extra agents have their own token costs; no fixed saving is promised.

Select a model from this tool's available choices, not another provider's alias.
When an unnamed Codex child is used, the native defaults apply; on other tools use
an explicit supported model when available, otherwise record inheritance.
Pass a small task-specific context. Full-history forks may force the parent model.
When a newly configured role is unavailable in an existing session, use a known
role with explicit model/effort only if that tool supports it, carrying the intended
instructions. Never claim registry hot reload or silently use a third-party preset.
Escalate once with evidence if the selected model cannot handle the task.

## Planner -> Generator -> Evaluator

For a substantive milestone, the integrator arranges these steps in dependency order:

1. Planner (`harness_planner`, or parent): produce the scoped sprint contract using
   approved specs. Complex design can use `task_architect`. Do not invent 200 features.
2. Evaluator (`harness_evaluator`): agree measurable acceptance before implementation.
3. Generator (`harness_generator`, or assigned `task_developer`): implement in owned
   files against that contract. Parallel writers use separate worktrees.
4. Independent Evaluator: assess the delivered behavior against the same contract,
   with relevant tests and evidence. For a critical boundary use `task_quality_guard`
   as the evaluator, not a duplicate reviewer. The integrator records the decision.

Keep roles separate from models: different roles can use the same balanced model
in separate contexts. No requirement to run three costly agents concurrently.
For a simple change, the parent performs planning, implementation and checking,
explicitly recorded as single-agent work, not independent evaluation.
Grok's named project agents can carry these stages. Built-in type selection and
tool access vary by release: verify the runtime before using the optional built-in
map. Read-only profiles lack test execution tools; the integrator supplies actual evidence.

## Delegation and handoff

Task briefs include purpose, exact paths/file owner, approved inputs, acceptance,
permission and cost limits, stop condition and expected output. Workers are not
alone: preserve others' edits; no recursive delegation by default. Read-only agents
must not edit, upload or spend. A prompt restriction is not a sandbox guarantee;
parent runtime permission overrides can supersede agent defaults.

Use sprint files for contracts and decisions, supported messages for short coordination.
The integrator maintains the project's existing assignments, handoff and progress
records. Report what the user can now do, verified limits and the next concrete
action in plain language. Immediately record human assistance when needed; do not
fabricate labels or let unrelated manual work stop independent development.

Record each meaningful delegation: role, requested and actual model/effort (or
unknown), runtime task ID, owned paths, evidence, result and next action. Actual
model evidence comes from execution metadata or the client's task view, never
from the agent saying its own name. Existing children need not switch models.

## Installation and verification

The installer does not launch models, create credentials, adjust the parent model,
weaken approvals, start servers or publish anything. Existing different agent files
or settings are refused before writes; reconcile conflicts with a reviewed diff.
Later tool adoption appends its own verified model table rows while preserving
existing choices; customized protocols require manual reconciliation. Backups
contain original bytes and a restore manifest. Repeat installation is
byte-identical. Repository ignores must exclude its `.cache/` backup directory.

Distinguish: files written -> runtime accepts config -> role is discoverable -> a
bounded task completed -> actual model verified. A failure at one step is recorded
as unverified, not converted to success. Skill installation does not automatically
register the skill in every already-running client.
