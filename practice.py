#!/usr/bin/env python3
"""Debugging-round practice runner.

    python practice.py list
    python practice.py start 1 [--minutes 45]
    python practice.py check 1
    python practice.py reset 1
    python practice.py verify all      # maintainer self-test (uses solutions/)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUNDS = ROOT / "rounds"
WORKSPACE = ROOT / "workspace"
SOLUTIONS = ROOT / "solutions"
STATE_FILE = ".practice.json"


def round_src(n: int) -> Path:
    matches = sorted(ROUNDS.glob(f"round{n}_*"))
    if not matches:
        sys.exit(f"no round {n} under {ROUNDS}")
    return matches[0]


def workspace_dir(n: int) -> Path:
    return WORKSPACE / f"round{n}"


def copy_round(n: int, dest: Path) -> None:
    shutil.copytree(
        round_src(n), dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache")
    )


def run_pytest(cwd: Path, extra: list[str] | None = None, quiet: bool = False) -> dict[str, int]:
    cmd = [sys.executable, "-m", "pytest", "-q", "--color=yes", *(extra or [])]
    if quiet:
        cmd[cmd.index("--color=yes")] = "--color=no"
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if proc.returncode not in (0, 1) and "No module named pytest" in proc.stderr:
        sys.exit("pytest is not installed for this interpreter; see README (pip install -r requirements.txt)")
    out = proc.stdout + proc.stderr
    if not quiet:
        print(out)
    plain = re.sub(r"\x1b\[[0-9;]*m", "", out)
    counts = {k: 0 for k in ("passed", "failed", "error")}
    for num, kind in re.findall(r"(\d+) (passed|failed|errors?)", plain):
        counts["error" if kind.startswith("error") else kind] = int(num)
    return counts


def fmt_elapsed(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def cmd_list(_: argparse.Namespace) -> None:
    for path in sorted(ROUNDS.glob("round*_*")):
        n = path.name[len("round")]
        ws = workspace_dir(int(n))
        status = "in progress" if ws.exists() else "not started"
        print(f"  {n}  {path.name:<32} {status}")


def cmd_start(args: argparse.Namespace) -> None:
    dest = workspace_dir(args.round)
    if dest.exists():
        sys.exit(f"{dest} already exists. Use `check` to continue or `reset` to start over.")
    WORKSPACE.mkdir(exist_ok=True)
    copy_round(args.round, dest)
    (dest / STATE_FILE).write_text(json.dumps({"started": time.time(), "minutes": args.minutes}))
    print((dest / "BRIEF.md").read_text())
    print("-" * 72)
    print(f"Workspace: {dest.relative_to(ROOT)}")
    print(f"Timer started: {args.minutes} minutes. Run `python practice.py check {args.round}` any time.")


def cmd_check(args: argparse.Namespace) -> None:
    dest = workspace_dir(args.round)
    if not dest.exists():
        sys.exit(f"round {args.round} not started; run `python practice.py start {args.round}`")
    counts = run_pytest(dest, args.pytest_args)
    total = sum(counts.values())
    print("=" * 72)
    print(f"Round {args.round}: {counts['passed']}/{total} passing", end="")
    if counts["failed"] or counts["error"]:
        print(f"  ({counts['failed']} failed, {counts['error']} errors)")
    else:
        print("  -- all green! Did you also handle the bug report in BRIEF.md?")
    state_path = dest / STATE_FILE
    if state_path.exists():
        state = json.loads(state_path.read_text())
        elapsed = time.time() - state["started"]
        limit = state["minutes"] * 60
        line = f"Elapsed {fmt_elapsed(elapsed)} / {fmt_elapsed(limit)}"
        if elapsed > limit:
            line += f"  ** OVER TIME by {fmt_elapsed(elapsed - limit)} **"
        print(line)


def cmd_reset(args: argparse.Namespace) -> None:
    dest = workspace_dir(args.round)
    if dest.exists() and not args.yes:
        answer = input(f"Delete your work in {dest.relative_to(ROOT)} and restore the buggy copy? [y/N] ")
        if answer.strip().lower() != "y":
            print("aborted")
            return
    shutil.rmtree(dest, ignore_errors=True)
    print(f"Removed {dest.relative_to(ROOT)}. Run `python practice.py start {args.round}` to begin again.")


def apply_patch(patch: Path, cwd: Path) -> None:
    proc = subprocess.run(
        ["patch", "-p1", "--quiet", "--forward", "-i", str(patch)],
        cwd=cwd, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"patch failed:\n{proc.stdout}{proc.stderr}")


def verify_one(n: int) -> bool:
    patch = SOLUTIONS / f"round{n}.patch"
    hidden = SOLUTIONS / "hidden_tests" / f"round{n}_test_hidden.py"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "r"
        copy_round(n, work)
        if hidden.exists():
            shutil.copy(hidden, work / "tests" / "test_hidden.py")

        buggy = run_pytest(work, quiet=True)
        hidden_buggy = run_pytest(work, ["tests/test_hidden.py"], quiet=True) if hidden.exists() else None
        apply_patch(patch, work)
        fixed = run_pytest(work, quiet=True)

    ok = buggy["failed"] + buggy["error"] > 0 and fixed["failed"] + fixed["error"] == 0
    if hidden_buggy is not None:
        ok = ok and hidden_buggy["failed"] > 0
    print(
        f"round {n}: buggy {buggy['passed']} passed / {buggy['failed']} failed"
        + (f" (hidden test fails: {hidden_buggy['failed'] > 0})" if hidden_buggy else "")
        + f" -> patched {fixed['passed']} passed / {fixed['failed']} failed"
        + ("  OK" if ok else "  PROBLEM")
    )
    return ok


def cmd_verify(args: argparse.Namespace) -> None:
    targets = (
        [int(p.name[len("round")]) for p in sorted(ROUNDS.glob("round*_*"))]
        if args.round == "all"
        else [int(args.round)]
    )
    results = [verify_one(n) for n in targets]
    sys.exit(0 if all(results) else 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="show rounds").set_defaults(func=cmd_list)

    p = sub.add_parser("start", help="copy a fresh buggy round into workspace/ and start the timer")
    p.add_argument("round", type=int)
    p.add_argument("--minutes", type=int, default=45)
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("check", help="run the tests in your workspace copy")
    p.add_argument("round", type=int)
    p.add_argument("pytest_args", nargs=argparse.REMAINDER, help="extra args passed to pytest (e.g. -x -k name)")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("reset", help="throw away your workspace copy")
    p.add_argument("round", type=int)
    p.add_argument("-y", "--yes", action="store_true", help="don't ask for confirmation")
    p.set_defaults(func=cmd_reset)

    p = sub.add_parser("verify", help="maintainer self-test: patch fixes every bug (SPOILER-free output)")
    p.add_argument("round", help="round number or 'all'")
    p.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
