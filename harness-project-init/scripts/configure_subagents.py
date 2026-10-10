#!/usr/bin/env python3
"""Merge project routing assets; dry-run by default, Python 3.11+, no network."""

import argparse
import hashlib
import json
import re
import sys
import tempfile
import tomllib
from datetime import UTC, datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- harness-project-init: model-routing -->"
END = "<!-- /harness-project-init: model-routing -->"
COMMON = (
    "Read the project's instructions and assigned contract. Stay within the approved "
    "scope, permissions, fee and phase gates. Do not delegate recursively. Return "
    "evidence, limits, a plain-language account of the outcome and the next action. "
    "Never mark an unverified feature passed or claim a model from its own description."
)
ROLES = {
    "task_explorer": (
        "Map relevant code and return file evidence; do not edit or run external actions.",
        False,
    ),
    "task_progress_monitor": (
        "Summarize changed progress and required human input from records; do not poll repeatedly or edit.",
        False,
    ),
    "task_developer": (
        "Implement the bounded assignment, preserve other contributors' edits and run relevant checks. Require explicit file ownership.",
        True,
    ),
    "task_reviewer": (
        "Independently review the assigned change for reproducible correctness and missing verification; do not edit.",
        False,
    ),
    "task_quality_guard": (
        "Review data, costs, persistence, concurrency and identity boundaries with concrete evidence; do not edit or trigger external actions.",
        False,
    ),
    "task_architect": (
        "Evaluate genuinely complex design against approved scope, compare alternatives and return a proposal; do not edit.",
        False,
    ),
    "harness_planner": (
        "Turn the approved request into a bounded sprint contract: scope, owner, inputs, acceptance and stop conditions. Do not invent a feature quota or expand approved scope. Return the proposal to the integrator; do not edit.",
        False,
    ),
    "harness_generator": (
        "Implement only the agreed sprint contract in assigned files. You are not alone: preserve other contributors' edits. Return behavior, checks, limits and handoff; do not approve your own work as independent evaluation.",
        True,
    ),
    "harness_evaluator": (
        "Independently compare delivered behavior and evidence with the agreed contract. Report pass, fail or unverified with reproduction and missing checks. Do not edit, upload or launch paid work; ask the integrator to run unavailable checks.",
        False,
    ),
}


class Conflict(ValueError):
    pass


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def merge_block(original, body):
    block = BEGIN + "\n" + body.rstrip() + "\n" + END
    if BEGIN in original or END in original:
        if original.count(BEGIN) != 1 or original.count(END) != 1:
            raise Conflict("Ambiguous managed instruction block")
        start, stop = original.index(BEGIN), original.index(END) + len(END)
        if stop < start:
            raise Conflict("Reversed managed block")
        existing = original[start:stop].replace("\r\n", "\n")
        if existing != block:
            raise Conflict("Managed instruction block differs; reconcile it before installation")
        return original
    return original + ("\n\n" if original and not original.endswith("\n\n") else "") + block + "\n"


def merge_toml(original, section, expected):
    parsed = tomllib.loads(original)
    current = parsed
    for name in section.split("."):
        current = current.get(name, {})
        if not isinstance(current, dict):
            raise Conflict(f"[{section}] is not a table")
    for key, value in expected.items():
        if key in current and (current[key] != value or type(current[key]) is not type(value)):
            raise Conflict(f"[{section}] {key} already has a different value")
    missing = {k: v for k, v in expected.items() if k not in current}
    if not missing:
        return original
    lines = "".join(
        f"{key} = {str(value).lower() if isinstance(value, bool) else quote(value)}\n"
        for key, value in missing.items()
    )
    header = re.search(r"(?m)^\s*\[" + re.escape(section) + r"\]\s*(?:#[^\n]*)?\r?$", original)
    if header:
        position = original.find("\n", header.end())
        position = len(original) if position < 0 else position + 1
        updated = (
            original[:position]
            + ("\n" if position == len(original) and not original.endswith("\n") else "")
            + lines
            + original[position:]
        )
    elif current:
        raise Conflict(f"[{section}] uses inline/dotted syntax; merge its missing keys manually")
    else:
        updated = (
            original
            + ("\n" if original and not original.endswith("\n") else "")
            + f"\n[{section}]\n"
            + lines
        )
    checked = tomllib.loads(updated)
    for name in section.split("."):
        checked = checked[name]
    if any(checked.get(k) != v for k, v in expected.items()):
        raise Conflict(f"Cannot safely merge [{section}]")
    return updated


def safe_target(root, relative):
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise Conflict(f"Target escapes selected root: {relative}")
    if target.exists() and not target.is_file():
        raise Conflict(f"Target is not a file: {relative}")
    return target


def merge_routing_document(original, incoming):
    if not original:
        return incoming
    delimiter = "\n## Configured model choices\n"
    normalized = original.replace("\r\n", "\n")
    incoming = incoming.replace("\r\n", "\n")
    if normalized.count(delimiter) != 1 or incoming.count(delimiter) != 1:
        raise Conflict("Existing routing document is not the expected generated protocol")
    prefix, old_table = normalized.split(delimiter)
    new_prefix, new_table = incoming.split(delimiter)
    if prefix.replace("\r\n", "\n") != new_prefix.replace("\r\n", "\n"):
        raise Conflict("Routing protocol was customized or upgraded; reconcile it first")

    def rows(table):
        lines = [line.strip() for line in table.splitlines() if line.strip()]
        if lines[:2] != ["| Tool | Role | Requested model | Effort |", "| --- | --- | --- | --- |"]:
            raise Conflict("Routing table header differs")
        result = {}
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split("|")]
            if len(cells) != 6 or cells[0] or cells[-1]:
                raise Conflict("Routing table contains a customized row")
            key, value = tuple(cells[1:3]), tuple(cells[3:5])
            if key in result:
                raise Conflict("Routing table has duplicate role rows")
            result[key] = value
        return result

    existing, requested = rows(old_table), rows(new_table)
    extra = []
    for key, value in requested.items():
        if key in existing and existing[key] != value:
            raise Conflict(f"Routing model choice differs: {'/'.join(key)}")
        if key not in existing:
            extra.append("| " + " | ".join((*key, *value)) + " |\n")
    newline = "\r\n" if "\r\n" in original else "\n"
    return (
        original
        if not extra
        else original.rstrip() + newline + "".join(extra).replace("\n", newline)
    )


def codex_role(name, model, effort):
    description, write = ROLES[name]
    return (
        f"name = {quote(name)}\ndescription = {quote(description)}\n"
        f"model = {quote(model)}\nmodel_reasoning_effort = {quote(effort)}\n"
        f"sandbox_mode = {quote('workspace-write' if write else 'read-only')}\n"
        f"developer_instructions = {quote(COMMON + ' ' + description)}\n"
    )


def claude_role(name, model):
    description, write = ROLES[name]
    tools = "Read, Glob, Grep, Bash, PowerShell, Edit, Write" if write else "Read, Glob, Grep"
    return (
        f"---\nname: {quote(name)}\ndescription: {quote(description)}\n"
        f"model: {quote(model)}\ntools: {tools}\n---\n\n{COMMON} {description}\n"
    )


def grok_role(name, model):
    description, write = ROLES[name]
    tools = "Read, Glob, Grep, Bash, PowerShell, Edit, Write" if write else "Read, Glob, Grep"
    return (
        f"---\nname: {quote(name)}\ndescription: {quote(description)}\n"
        f"model: {quote(model)}\nprompt_mode: full\n"
        f"permission_mode: {'default' if write else 'plan'}\nagents_md: true\n"
        f"tools: {tools}\n---\n\n{COMMON} {description}\n"
    )


def make_plan(project, tools, preset, grok_home=None, grok_models=None):
    if not project.is_dir():
        raise Conflict("The selected project directory must already exist")
    safe_target(project, ".cache/harness-agent-routing/backups/restore.json")
    planned = {}

    def add(root, relative, content, merge=None):
        target = safe_target(root, relative)
        original = target.read_bytes() if target.exists() else None
        text = original.decode("utf-8-sig") if original is not None else ""
        if merge:
            result = merge(text, content)
            data = original if result == text and original is not None else result.encode("utf-8")
        else:
            data = content.encode("utf-8")
            if original is not None and text.replace("\r\n", "\n") != content.replace("\r\n", "\n"):
                raise Conflict(f"Existing file differs; no replacement: {relative}")
            if original is not None:
                data = original
        planned[target] = (original, data)

    protocol = (SKILL_ROOT / "references/project-routing-template.md").read_text(encoding="utf-8")
    table = [
        "\n## Configured model choices\n",
        "| Tool | Role | Requested model | Effort |",
        "| --- | --- | --- | --- |",
    ]
    for tool in ("codex", "claude"):
        if tool in tools:
            for name in ROLES:
                choice = preset[tool][name]
                model, effort = choice if tool == "codex" else (choice, "runtime default")
                if not isinstance(model, str) or not model.strip():
                    raise Conflict(f"Missing {tool} model for {name}")
                table.append(f"| {tool} | {name} | {model} | {effort} |")
    grok_named = False
    if grok_models is not None:
        grok_named = set(grok_models) == set(ROLES)
        if (not grok_named and set(grok_models) != {"explore", "plan", "general-purpose"}) or any(
            not isinstance(v, str) or not v.strip() for v in grok_models.values()
        ):
            raise Conflict(
                "Grok map must provide all nine named roles, or explore/plan/general-purpose IDs"
            )
        if not grok_named and not grok_home:
            raise Conflict("Grok built-in model map is user-scoped: explicitly provide --grok-home")
        for name, model in grok_models.items():
            table.append(f"| grok | {name} | {model} | runtime default |")
    add(
        project, "docs/agent-routing.md", protocol + "\n".join(table) + "\n", merge_routing_document
    )
    pointer = (
        "## Capability-based agent routing\n\n"
        "Read `docs/agent-routing.md` before delegating. Use the selected tool's actual model IDs, "
        "bounded fresh context, explicit file ownership and no recursive delegation. "
        "Use Planner -> Generator -> independent Evaluator for substantive milestones; "
        "simple work stays in the parent with separate planning and checking passes, "
        "recorded as single-agent work. Configuration alone does not prove execution or savings."
    )
    add(project, "AGENTS.md", pointer, merge_block)
    status = {}
    if "codex" in tools:
        default_model, default_effort = preset["codex_default"]
        codex_path = safe_target(project, ".codex/config.toml")
        existing_agents = (
            tomllib.loads(codex_path.read_text(encoding="utf-8-sig")).get("agents", {})
            if codex_path.exists()
            else {}
        )
        concurrency = (
            {}
            if any(
                key in existing_agents
                for key in ("max_threads", "max_concurrent_threads_per_session")
            )
            else {"max_concurrent_threads_per_session": 3}
        )
        add(
            project,
            ".codex/config.toml",
            {
                "enabled": True,
                **concurrency,
                "default_subagent_model": default_model,
                "default_subagent_reasoning_effort": default_effort,
            },
            lambda old, wanted: merge_toml(old, "agents", wanted),
        )
        for name in ROLES:
            add(project, f".codex/agents/{name}.toml", codex_role(name, *preset["codex"][name]))
        status["codex"] = (
            "native-files; availability, discovery and execution still require verification"
        )
    if "claude" in tools:
        for name in ROLES:
            add(project, f".claude/agents/{name}.md", claude_role(name, preset["claude"][name]))
        add(project, "CLAUDE.md", pointer, merge_block)
        status["claude"] = (
            "native-files; aliases resolve under the account/provider; execution not tested"
        )
    if "grok" in tools:
        status["grok"] = "portable-protocol; native model map not requested"
        if grok_named:
            for name in ROLES:
                add(project, f".grok/agents/{name}.md", grok_role(name, grok_models[name]))
            status["grok"] = (
                "native-project-agent files; inspect and execution still require verification"
            )
        elif grok_models:
            add(
                grok_home,
                "config.toml",
                grok_models,
                lambda old, wanted: merge_toml(old, "subagents.models", wanted),
            )
            status["grok"] = (
                "native-user-map for built-in types; inspect and execution still require verification"
            )
    if "portable" in tools:
        status["portable"] = "instruction-protocol; no native model selection claimed"
    return planned, status


def apply_plan(planned, backup_root):
    changed = {p: (old, new) for p, (old, new) in planned.items() if old != new}
    if not changed:
        return None
    for path, (old, _) in planned.items():
        actual = path.read_bytes() if path.exists() else None
        if actual != old:
            raise Conflict(f"File changed after planning: {path.name}")
    backup = backup_root / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    backup.mkdir(parents=True, exist_ok=False)
    manifest = []
    for number, (path, (old, new)) in enumerate(changed.items()):
        saved = backup / f"{number}.original"
        if old is not None:
            saved.write_bytes(old)
        manifest.append(
            {
                "target": str(path),
                "original": str(saved) if old is not None else None,
                "new_sha256": hashlib.sha256(new).hexdigest(),
            }
        )
    (backup / "restore.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    written = []
    try:
        for path, (old, new) in changed.items():
            if (path.read_bytes() if path.exists() else None) != old:
                raise Conflict(f"Concurrent change before writing: {path.name}")
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
                temp.write(new)
                temporary = Path(temp.name)
            try:
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
            written.append(path)
    except Exception:
        for path in reversed(written):
            old, new = changed[path]
            try:
                if path.read_bytes() != new:
                    continue  # Never overwrite a concurrent contributor during rollback.
                if old is None:
                    path.unlink()
                else:
                    path.write_bytes(old)
            except OSError:
                continue  # Preserve a concurrent deletion; still restore other files.
        raise
    return str(backup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--tools", nargs="+", choices=["codex", "claude", "grok", "portable"], required=True
    )
    parser.add_argument("--preset", type=Path, default=SKILL_ROOT / "assets/routing-presets.json")
    parser.add_argument("--grok-home", type=Path)
    parser.add_argument("--grok-models", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.grok_models and "grok" not in args.tools:
        parser.error("--grok-models requires --tools grok")
    try:
        preset = json.loads(args.preset.read_text(encoding="utf-8-sig"))
        models = (
            json.loads(args.grok_models.read_text(encoding="utf-8-sig"))
            if args.grok_models
            else None
        )
        project = args.project.resolve()
        planned, status = make_plan(
            project,
            args.tools,
            preset,
            args.grok_home.resolve() if args.grok_home else None,
            models,
        )
        changed = [str(p) for p, (old, new) in planned.items() if old != new]
        backup = (
            apply_plan(planned, project / ".cache/harness-agent-routing/backups")
            if args.apply
            else None
        )
        print(
            json.dumps(
                {
                    "mode": "applied" if args.apply else "dry-run",
                    "changed": changed,
                    "backup": backup,
                    "support": status,
                    "runtime_verified": False,
                    "model_requests": 0,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(
            json.dumps({"status": "refused-or-failed", "reason": str(error)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
