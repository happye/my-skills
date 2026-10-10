#!/usr/bin/env python3
"""Offline installer behavior tests; no personal config or model calls."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from configure_subagents import (
    SKILL_ROOT,
    Conflict,
    apply_plan,
    make_plan,
    merge_block,
    merge_toml,
)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.project = self.root / "项目 space"
        self.project.mkdir()
        self.preset = json.loads(
            (SKILL_ROOT / "assets/routing-presets.json").read_text(encoding="utf-8")
        )

    def tearDown(self):
        self.directory.cleanup()

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in self.root.rglob("*")
            if p.is_file()
        }

    def test_dry_run_then_apply_and_byte_identical_second_install(self):
        config = self.project / ".codex/config.toml"
        config.parent.mkdir()
        original = b'\xef\xbb\xbfmodel = "parent-choice"\r\n# keep this\r\n[agents]\r\nenabled = true\r\n[other]\r\nvalue = 17\r\n'
        config.write_bytes(original)
        (self.project / "AGENTS.md").write_text("User rules stay.\n", encoding="utf-8")
        before = self.snapshot()
        planned, status = make_plan(self.project, ["codex", "claude", "grok"], self.preset)
        self.assertEqual(before, self.snapshot())
        self.assertIn("portable-protocol", status["grok"])
        backup = apply_plan(planned, self.project / ".cache/backups")
        self.assertIsNotNone(backup)
        updated = config.read_text(encoding="utf-8")
        self.assertIn('model = "parent-choice"', updated)
        self.assertIn("# keep this", updated)
        self.assertIn("[other]\nvalue = 17", updated)
        import tomllib

        parsed = tomllib.loads(updated)
        self.assertEqual(parsed["agents"]["max_concurrent_threads_per_session"], 3)
        roles = list((self.project / ".codex/agents").glob("*.toml"))
        self.assertEqual(len(roles), 9)
        for file in roles:
            role = tomllib.loads(file.read_text(encoding="utf-8"))
            self.assertEqual(role["model"], self.preset["codex"][role["name"]][0])
            self.assertIn("developer_instructions", role)
        readonly = (self.project / ".claude/agents/harness_evaluator.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("tools: Read, Glob, Grep\n", readonly)
        self.assertNotIn("Bash", readonly)
        self.assertNotIn("effort:", readonly)
        manifest = json.loads((Path(backup) / "restore.json").read_text())
        saved = next(entry for entry in manifest if entry["target"] == str(config))
        self.assertEqual(Path(saved["original"]).read_bytes(), original)
        first = self.snapshot()
        second, _ = make_plan(self.project, ["codex", "claude", "grok"], self.preset)
        self.assertIsNone(apply_plan(second, self.project / ".cache/backups"))
        self.assertEqual(first, self.snapshot())

    def test_agent_conflict_refuses_all_writes(self):
        target = self.project / ".claude/agents/task_developer.md"
        target.parent.mkdir(parents=True)
        target.write_text("Existing customized agent", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaises(Conflict):
            make_plan(self.project, ["codex", "claude"], self.preset)
        self.assertEqual(before, self.snapshot())

    def test_config_conflict_and_inline_conflict(self):
        with self.assertRaises(Conflict):
            merge_toml("[agents]\nenabled = false\n", "agents", {"enabled": True})
        with self.assertRaises(Conflict):
            merge_toml(
                "agents = {enabled = true}\n",
                "agents",
                {"enabled": True, "default_subagent_model": "small"},
            )
        self.assertEqual(
            merge_toml("[agents]\nenabled = true\n", "agents", {"enabled": True}),
            "[agents]\nenabled = true\n",
        )

    def test_managed_block_conflicts(self):
        written = merge_block("My instruction\n", "Managed rule")
        self.assertEqual(merge_block(written, "Managed rule"), written)
        with self.assertRaises(Conflict):
            merge_block(written, "Different rule")
        with self.assertRaises(Conflict):
            merge_block(written + written, "Managed rule")

    def test_grok_routes_only_in_explicit_user_scope(self):
        models = {
            "explore": "verified-fast",
            "plan": "verified-planner",
            "general-purpose": "verified-code",
        }
        before = self.snapshot()
        with self.assertRaises(Conflict):
            make_plan(self.project, ["grok"], self.preset, grok_models=models)
        self.assertEqual(before, self.snapshot())
        grok_home = self.root / "selected-grok-home"
        grok_home.mkdir()
        (grok_home / "config.toml").write_text(
            '[models]\ndefault = "keep-main"\n', encoding="utf-8"
        )
        plan, _ = make_plan(self.project, ["grok"], self.preset, grok_home, models)
        apply_plan(plan, self.project / ".cache/backups")
        import tomllib

        data = tomllib.loads((grok_home / "config.toml").read_text())
        self.assertEqual(data["models"]["default"], "keep-main")
        self.assertEqual(data["subagents"]["models"], models)
        self.assertFalse((self.project / ".grok/config.toml").exists())

    def test_concurrent_change_preserved(self):
        plan, _ = make_plan(self.project, ["portable"], self.preset)
        (self.project / "AGENTS.md").write_text("Concurrent contributor", encoding="utf-8")
        with self.assertRaises(Conflict):
            apply_plan(plan, self.project / ".cache/backups")
        self.assertEqual((self.project / "AGENTS.md").read_text(), "Concurrent contributor")
        self.assertFalse((self.project / "docs").exists())

    def test_grok_named_roles_need_no_personal_write(self):
        from configure_subagents import ROLES

        models = {
            name: "verified-code" if name.startswith("harness_") else "verified-fast"
            for name in ROLES
        }
        plan, status = make_plan(self.project, ["grok"], self.preset, grok_models=models)
        apply_plan(plan, self.project / ".cache/backups")
        self.assertIn("native-project-agent", status["grok"])
        self.assertEqual(len(list((self.project / ".grok/agents").glob("*.md"))), 9)
        role = (self.project / ".grok/agents/harness_evaluator.md").read_text(encoding="utf-8")
        self.assertIn('model: "verified-code"', role)
        self.assertIn("permission_mode: plan", role)
        self.assertIn("tools: Read, Glob, Grep\n", role)
        self.assertFalse((self.project / ".grok/config.toml").exists())

    def test_later_tool_adoption_preserves_existing_choices(self):
        first, _ = make_plan(self.project, ["codex"], self.preset)
        apply_plan(first, self.project / ".cache/backups")
        config = (self.project / ".codex/config.toml").read_bytes()
        second, _ = make_plan(self.project, ["claude"], self.preset)
        apply_plan(second, self.project / ".cache/backups")
        self.assertEqual((self.project / ".codex/config.toml").read_bytes(), config)
        table = (self.project / "docs/agent-routing.md").read_text()
        self.assertIn("| codex | task_developer | gpt-6.1-sol | medium |", table)
        self.assertIn("| claude | task_developer | sonnet | runtime default |", table)
        again, _ = make_plan(self.project, ["codex", "claude"], self.preset)
        self.assertIsNone(apply_plan(again, self.project / ".cache/backups"))

    def test_existing_concurrency_caps_preserved(self):
        import tomllib

        config = self.project / ".codex/config.toml"
        config.parent.mkdir()
        for key in ["max_threads", "max_concurrent_threads_per_session"]:
            config.write_text(f"[agents]\n{key} = 1\n", encoding="utf-8")
            plan, _ = make_plan(self.project, ["codex"], self.preset)
            parsed = tomllib.loads(plan[config][1].decode())
            self.assertEqual(parsed["agents"][key], 1)
            alternate = (
                "max_threads" if key != "max_threads" else "max_concurrent_threads_per_session"
            )
            self.assertNotIn(alternate, parsed["agents"])

    def test_crlf_repeat_install_is_byte_identical_and_tool_adoption_works(self):
        first, _ = make_plan(self.project, ["codex"], self.preset)
        apply_plan(first, self.project / ".cache/backups")
        for path in self.project.rglob("*"):
            if path.is_file() and ".cache" not in path.parts:
                path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        before = self.snapshot()
        repeat, _ = make_plan(self.project, ["codex"], self.preset)
        self.assertIsNone(apply_plan(repeat, self.project / ".cache/backups"))
        self.assertEqual(before, self.snapshot())
        extra, _ = make_plan(self.project, ["claude"], self.preset)
        apply_plan(extra, self.project / ".cache/backups")
        data = (self.project / "docs/agent-routing.md").read_bytes()
        self.assertIn(b"| claude |", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

    def test_rollback_keeps_concurrent_deletion_and_restores_other_paths(self):
        a, b, c = [self.project / name for name in ["a", "b", "c"]]
        a.write_bytes(b"old-a")
        plan = {a: (b"old-a", b"new-a"), b: (None, b"new-b"), c: (None, b"new-c")}
        real_replace = Path.replace

        def fail_third(source, target):
            if target == c:
                b.unlink()
                raise OSError("concurrent deletion plus failure")
            return real_replace(source, target)

        with patch.object(Path, "replace", fail_third):
            with self.assertRaises(OSError):
                apply_plan(plan, self.project / ".cache/backups")
        self.assertEqual(a.read_bytes(), b"old-a")
        self.assertFalse(b.exists())
        self.assertFalse(c.exists())

    def test_rollback_restores_written_files_after_replace_failure(self):
        (self.project / "AGENTS.md").write_text("Existing rules", encoding="utf-8")
        plan, _ = make_plan(self.project, ["codex"], self.preset)
        real_replace = Path.replace
        calls = 0

        def fail_second(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated write failure")
            return real_replace(source, target)

        with patch.object(Path, "replace", fail_second):
            with self.assertRaises(OSError):
                apply_plan(plan, self.project / ".cache/backups")
        self.assertFalse((self.project / "docs/agent-routing.md").exists())
        self.assertEqual((self.project / "AGENTS.md").read_text(), "Existing rules")
        self.assertFalse((self.project / ".codex/config.toml").exists())

    def test_symlink_escape_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.project / "docs").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit this fixture symlink")
        with self.assertRaises(Conflict):
            make_plan(self.project, ["portable"], self.preset)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
