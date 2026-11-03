#!/usr/bin/env python3
"""Keep a questions file and its optional review copy in step.

    questions.py status <file.md>
    questions.py pull   <file.md> <copy.md>             # copy the user's answers into the file
    questions.py push   <file.md> <copy.md> [--meta KEY=VALUE ...]
                                                        # rewrite the review copy from the file

The review copy is a markdown file the user edits wherever their client lets them answer (for
example a client's review or artifact surface). `push` keeps the copy's existing frontmatter; for a
new copy it writes frontmatter only from --meta pairs, in the order given (the client's own
instructions say which keys it needs).

A question is a heading `### <ID>. <title>` (ID like T1, R12) followed by its text and a line
`**Your answer:**`; the answer is everything after that line up to the next heading or `---`.
`pull` changes only answer blocks, matched by ID, and reports what changed. `push` refuses while the
review copy holds an answer the file lacks, so a push can never overwrite unsynced answers.
Only the standard library is used.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HEADING = re.compile(r"^#{2,4}\s+\\?\*{0,2}([A-Z]{1,3}\d+)\\?\*{0,2}\s*[.:)]", re.M)
ANY_HEADING = re.compile(r"^#{1,6}\s")
MARKER = re.compile(r"^\s*(?:>\s*)?[*_]{0,2}your answer[*_:]{0,4}\s*[*_]{0,2}\s*:?\s*\\?\s*$", re.I)
PLACEHOLDER = "(answer here)"  # not italic: an editor keeps the style for whatever is typed over it
OLD_PLACEHOLDERS = ("_(answer here)_", r"\_(answer here)\_")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def body(text: str) -> tuple[str, str]:
    m = FRONTMATTER.match(text)
    return (m.group(0), text[m.end():]) if m else ("", text)


def blocks(text: str) -> dict[str, tuple[int, int]]:
    """ID -> (start, end) character span of the answer block (the lines after the marker)."""
    lines = text.splitlines(keepends=True)
    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)
    offsets.append(pos)
    found, current, i = {}, None, 0
    while i < len(lines):
        m = HEADING.match(lines[i])
        if m:
            current = m.group(1)
        elif current and MARKER.match(lines[i]):
            j = i + 1
            while (j < len(lines) and not ANY_HEADING.match(lines[j]) and lines[j].strip() != "---"
                   and not lines[j].lstrip("\\ ").startswith("→")):  # "→ Settled:" ends the answer
                j += 1
            found[current] = (offsets[i + 1], offsets[j])
            current = None
            i = j
            continue
        i += 1
    return found


def clean(answer: str) -> str:
    """The answer as meaning, not formatting: drop the placeholder, editor hard breaks, blank edges."""
    out = []
    for line in answer.splitlines():
        line = line.rstrip()
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        for old in OLD_PLACEHOLDERS:
            line = line.replace(old, "")
        line = line.replace("\\_", "_").replace("\\*", "*").replace(r"\(answer here\)", "").replace(PLACEHOLDER, "")
        stripped = line.strip()
        if stripped in {"()", "_()_"} or (stripped and set(stripped) <= set("*_>\\ ")):
            line = ""  # only markup left, e.g. an emptied italic placeholder saved as `\*\*`
        out.append(line)
    text = "\n".join(out).strip()
    for mark in ("*", "_"):  # an answer typed over an italic placeholder comes back wrapped in one
        if len(text) > 2 and text[0] == mark == text[-1] and mark not in text[1:-1]:
            text = text[1:-1].strip()
    return text


def answers(text: str) -> dict[str, str]:
    return {qid: clean(text[a:b]) for qid, (a, b) in blocks(text).items()}


def status(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    got = answers(text)
    open_ids = [q for q, a in got.items() if not a]
    print(f"{len(got)} questions, {len(got) - len(open_ids)} answered, {len(open_ids)} open")
    if open_ids:
        print("open:", " ".join(open_ids))
    missing = sorted(set(HEADING.findall(text)) - set(got))
    if missing:
        print("no answer line:", " ".join(missing))
    return 0


def pull(path: Path, artifact: Path) -> int:
    text = path.read_text(encoding="utf-8")
    theirs = answers(body(artifact.read_text(encoding="utf-8"))[1])
    spans = blocks(text)
    changed = []
    for qid, (a, b) in sorted(spans.items(), key=lambda kv: -kv[1][0]):
        new = theirs.get(qid)
        if not new or new == clean(text[a:b]):  # a blank in the review copy never erases an answer
            continue
        block = "\n" + new + "\n\n"
        text = text[:a] + block + text[b:]
        changed.append(qid)
    unknown = sorted(set(theirs) - set(spans))
    if changed:
        path.write_text(text, encoding="utf-8")
    print("updated:", " ".join(sorted(changed)) if changed else "nothing")
    if unknown:
        print("in the review copy but not the file (left alone):", " ".join(unknown))
    return 0


def repo_relative(path: Path) -> str:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path.resolve().parent,
                         capture_output=True, text=True)
    if out.returncode == 0:
        try:
            return path.resolve().relative_to(Path(out.stdout.strip())).as_posix()
        except ValueError:
            pass
    return path.resolve().as_posix()


def push(path: Path, artifact: Path, meta: list[str]) -> int:
    text = path.read_text(encoding="utf-8")
    mine = answers(text)
    if artifact.exists():
        front, rest = body(artifact.read_text(encoding="utf-8"))
        theirs = answers(rest)
        unsynced = [q for q, a in theirs.items() if a and a != mine.get(q)]
        if unsynced:
            print("refused: the review copy has answers the file lacks:", " ".join(unsynced),
                  "\nRun pull first.", file=sys.stderr)
            return 1
    else:
        front = ""
    if not front and meta:
        pairs = []
        for item in meta:
            key, sep, value = item.partition("=")
            if not sep or not key.strip():
                print(f"--meta takes KEY=VALUE, got {item!r}", file=sys.stderr)
                return 64
            pairs.append(f"{key.strip()}: {value.strip()}")
        front = "---\n" + "\n".join(pairs) + "\n---\n"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    note = (f"> Repository copy: `{repo_relative(path)}`. Write your answers here, under each "
            "**Your answer:**, then tell the session you are done.\n\n")
    artifact.write_text(front + ("\n" if front else "") + note + text, encoding="utf-8")
    print(f"pushed {len(mine)} questions to {artifact}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="questions.py", description=__doc__.split("\n\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__.split("\n\n", 1)[1])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("status"); p.add_argument("file", type=Path)
    p = sub.add_parser("pull"); p.add_argument("file", type=Path); p.add_argument("copy", type=Path)
    p = sub.add_parser("push"); p.add_argument("file", type=Path); p.add_argument("copy", type=Path)
    p.add_argument("--meta", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args(argv)
    if args.command == "status":
        return status(args.file)
    if args.command == "pull":
        return pull(args.file, args.copy)
    return push(args.file, args.copy, args.meta)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
