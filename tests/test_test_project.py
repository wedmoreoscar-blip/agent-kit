"""tools/test-project (related, recorded, full), prepare-worktree's readiness check, and the
baseline block's rendering of test_related.

Run from the kit root: python3 -m unittest discover -s tests
Standard library only. Each case builds a throwaway git repository holding a copy of the core
tools and a minimal profile, so nothing here touches a real project.
"""
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
TOOLS = KIT / "packs/core/files/tools"
BLOCKS = KIT / "packs/core/skills/writespec/blocks"

PROFILE = """\
# Project profile — test

```toml
[commands]
install_fresh = "true"
install_incr  = "true"
test          = "echo WHOLE-SUITE"
{extra}
[profiles]
quick = ["test"]
full  = ["test"]

[implementer]
run     = [{run}]
skip    = []
forbid  = []
blocked = []

[worktree]
copy_files       = []
dependency_files = []
```
"""


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)


class Repo:
    def __init__(self, extra: str = 'test_related = "echo RELATED {files}"\n'
                                    'test_collect = "echo COLLECTED"',
                 run: str = '"test_related"'):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        shutil.copytree(TOOLS, self.root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(BLOCKS, self.root / ".claude/skills/writespec/blocks")
        (self.root / "docs").mkdir()
        (self.root / "docs/project_profile.md").write_text(PROFILE.format(extra=extra, run=run))
        (self.root / "src").mkdir()
        (self.root / "src/a.py").write_text("a = 1\n")
        (self.root / "src/b.py").write_text("b = 1\n")
        (self.root / ".gitignore").write_text("__pycache__/\n")  # as the core gitignore block has
        for cmd in (["git", "init", "-q", "-b", "main"],
                    ["git", "config", "user.email", "kit@example.invalid"],
                    ["git", "config", "user.name", "kit"],
                    ["git", "add", "-A"], ["git", "commit", "-qm", "init"]):
            sh(*cmd, cwd=self.root)

    def git(self, *args: str) -> str:
        return sh("git", *args, cwd=self.root).stdout.strip()

    def tool(self, *args: str, name: str = "test-project") -> subprocess.CompletedProcess:
        return sh(sys.executable, str(self.root / "tools" / name), *args, cwd=self.root)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def close(self) -> None:
        self.tmp.cleanup()


class Related(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_passes_committed_unstaged_and_untracked_changes_but_nothing_else(self):
        r = self.repo
        r.git("checkout", "-qb", "leg")
        (r.root / "src/a.py").write_text("a = 2\n")
        r.commit("leg work")
        (r.root / "src/b.py").write_text("b = 2\n")       # unstaged
        (r.root / "src/new_test.py").write_text("x\n")    # untracked
        out = r.tool("related")
        self.assertEqual(out.returncode, 0, out.stderr)
        line = next(l for l in out.stdout.splitlines() if l.startswith("RELATED"))
        self.assertEqual(line, "RELATED src/a.py src/b.py src/new_test.py")

    def test_nothing_changed_runs_nothing(self):
        out = self.repo.tool("related")
        self.assertEqual(out.returncode, 0)
        self.assertIn("SKIP test_related", out.stdout)
        self.assertNotIn("RELATED", out.stdout.replace("SKIP test_related", ""))

    def test_explicit_files_are_shell_quoted(self):
        out = self.repo.tool("related", "--", "src/a.py", "has space.py")
        self.assertIn("RELATED src/a.py has space.py", out.stdout)
        self.assertIn("'has space.py'", out.stdout)  # the RUN line shows the quoting

    def test_base_head_parent_selects_only_the_leg_just_merged(self):
        r = self.repo
        r.git("checkout", "-qb", "leg1")
        (r.root / "src/a.py").write_text("a = 2\n")
        r.commit("leg1")
        r.git("checkout", "-q", "main")
        r.git("checkout", "-qb", "leg2")
        (r.root / "src/b.py").write_text("b = 2\n")
        r.commit("leg2")
        r.git("checkout", "-q", "main")
        r.git("checkout", "-qb", "integration")
        r.git("merge", "-q", "--no-ff", "--no-edit", "leg1")
        r.git("merge", "-q", "--no-ff", "--no-edit", "leg2")
        out = r.tool("related", "--base", "HEAD^1")
        self.assertIn("RELATED src/b.py", out.stdout)
        self.assertNotIn("src/a.py", out.stdout.split("RELATED", 1)[-1])

    def test_without_test_related_it_runs_the_whole_suite_and_says_so(self):
        self.repo.close()
        self.repo = Repo(extra="", run='"test"')
        out = self.repo.tool("related")
        self.assertEqual(out.returncode, 0)
        self.assertIn("NOTE no [commands].test_related", out.stdout)
        self.assertIn("WHOLE-SUITE", out.stdout)


class Recorded(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_clean_full_run_is_recorded_and_read_back_for_main(self):
        out = self.repo.tool("full")
        self.assertIn("RECORDED full baseline", out.stdout)
        shown = self.repo.tool("recorded")
        self.assertEqual(shown.returncode, 0, shown.stdout)
        self.assertIn("PASS test: echo WHOLE-SUITE", shown.stdout)
        self.assertIn("    WHOLE-SUITE", shown.stdout)

    def test_the_record_is_shared_with_other_worktrees(self):
        self.repo.tool("full")
        wt = self.repo.root.parent / "wt"
        self.repo.git("worktree", "add", "-q", "-b", "leg", str(wt))
        out = sh(sys.executable, str(wt / "tools/test-project"), "recorded", cwd=wt)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_a_failing_command_is_recorded_as_a_failure(self):
        self.repo.close()
        self.repo = Repo(extra='lint = "echo 21 problems; false"', run='"test"')
        profile = self.repo.root / "docs/project_profile.md"
        profile.write_text(profile.read_text().replace('full  = ["test"]', 'full  = ["test", "lint"]'))
        self.repo.commit("lint in full")
        self.assertNotEqual(self.repo.tool("full").returncode, 0)
        shown = self.repo.tool("recorded")
        self.assertEqual(shown.returncode, 0)
        self.assertIn("FAIL (exit 1) lint", shown.stdout)
        self.assertIn("21 problems", shown.stdout)

    def test_stale_once_main_moves(self):
        self.repo.tool("full")
        (self.repo.root / "src/a.py").write_text("a = 3\n")
        self.repo.commit("inline commit")
        out = self.repo.tool("recorded")
        self.assertEqual(out.returncode, 1)
        self.assertIn("STALE", out.stdout)

    def test_no_record_and_dirty_tree(self):
        self.assertIn("NO RECORD", self.repo.tool("recorded").stdout)
        (self.repo.root / "src/a.py").write_text("a = 4\n")
        self.assertIn("NOT RECORDED", self.repo.tool("full").stdout)
        self.assertEqual(self.repo.tool("recorded").returncode, 1)

    def test_stale_when_the_full_profile_changes(self):
        self.repo.tool("full")
        profile = self.repo.root / "docs/project_profile.md"
        profile.write_text(profile.read_text().replace('full  = ["test"]', 'full  = ["test", "test"]'))
        out = self.repo.tool("recorded")
        self.assertEqual(out.returncode, 1)
        self.assertIn("full profile has changed", out.stdout)


class ProfileAndBlocks(unittest.TestCase):
    def test_baseline_block_names_test_project_related(self):
        repo = Repo()
        try:
            out = repo.tool("baseline", name="spec-block")
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("- `tools/test-project related` (only the tests", out.stdout)
            self.assertNotIn("echo RELATED", out.stdout)
        finally:
            repo.close()

    def test_reserved_profile_names_are_rejected(self):
        repo = Repo()
        try:
            profile = repo.root / "docs/project_profile.md"
            profile.write_text(profile.read_text().replace('quick = ["test"]', 'related = ["test"]'))
            out = repo.tool("full")
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("reserved by tools/test-project", out.stderr)
        finally:
            repo.close()


class PrepareWorktree(unittest.TestCase):
    def run_prepare(self, repo: Repo) -> subprocess.CompletedProcess:
        wt = repo.root.parent / "wt"
        repo.git("worktree", "add", "-q", "-b", "leg", str(wt))
        return sh(sys.executable, str(repo.root / "tools/prepare-worktree"), str(wt), cwd=repo.root)

    def test_uses_test_collect_not_the_whole_suite(self):
        repo = Repo()
        try:
            out = self.run_prepare(repo)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("COLLECTED", out.stdout)
            self.assertIn("PASS test_collect", out.stdout)
            self.assertNotIn("WHOLE-SUITE", out.stdout)
        finally:
            repo.close()

    def test_falls_back_to_the_whole_suite_and_says_so(self):
        repo = Repo(extra="", run='"test"')
        try:
            out = self.run_prepare(repo)
            self.assertIn("NOTE no [commands].test_collect", out.stdout)
            self.assertIn("WHOLE-SUITE", out.stdout)
        finally:
            repo.close()


if __name__ == "__main__":
    unittest.main()
