---
name: questions
description: Collect every question the user must answer into one questions file (tasks/questions/<topic>.md, one per lane when several sessions run in parallel) with answer space, optionally mirrored to a review copy the user answers in; then pull the answers back and act on them. Use whenever a reply would ask the user more than one or two questions (planning, design choices, open agenda items), when the user says they have answered the questions, or asks to add, list or find questions.
---

# Questions file

One file collects every question for the user on a topic, so nothing is lost in chat scrollback.
Questions are appended over time and never deleted; answered ones stay as the record.

**Do not use** for a single yes/no or a quick clarification: ask that in chat.

## Files

- Canonical: `tasks/questions/<topic>.md`, kebab-case. When several orchestrator sessions run in
  parallel (`docs/project_profile.md` declares `[lanes]`; see
  `docs/workflows/parallel_sessions.md`), each lane owns `tasks/questions/<lane>.md` and uses only
  that file. Otherwise reuse an existing file whose topic fits before starting a new one.
- Review copy (optional): when your client gives the user somewhere to read and edit a markdown
  file outside the repository (a review or artifact surface; its own instructions say where such
  files go and which frontmatter they need), mirror the questions file there and let the user
  answer in it. Without one, the user answers in the repository file directly, and `pull`/`push`
  are not needed.
- `scripts/questions.py` (this skill's folder) does the deterministic parts: `status`, `pull`,
  `push` (`--meta KEY=VALUE` writes a new review copy's frontmatter). Run it with the project's
  Python.

## Format

Start a new file from [references/template.md](references/template.md). Each round of questions is
a `## <date> — <topic>` section; each question:

```markdown
### Q3. <short title>

<Context in two or three plain sentences: what it decides and why it matters now.>

- **(a)** <option> — <consequence>. *(recommended: <one-line reason>)*
- **(b)** <option> — <consequence>.

**Your answer:**

(answer here)

```

- IDs are a prefix of one to three capital letters plus a number, unique in the file, never reused
  or renumbered. The prefix is fixed per file and stated in its header: the lane's `prefix` from
  the profile when lanes are declared, otherwise `Q` or the topic's initial. Refer to questions by
  ID in chat.
- Each question stands alone: no "as above", no reliance on chat context.
- Put a recommendation on any question that has one; leave free-text questions (lists, preferences)
  open with an example of the expected shape.
- Order by what blocks the work first.

## Asking

1. If a review copy exists, `pull` first, so answers already given are not overwritten.
2. Append the new section to the repository file; `push` to the review copy if there is one.
3. In chat: one line per new question (ID and title) and where to answer (the review copy's name,
   or the repository path). Do not repeat the full questions in chat.

## When the user says they have answered

1. `pull` from the review copy, if there is one. Also read any comments the user left on it, in
   whatever form the client stores them, and resolve them as the client's instructions describe.
2. `status` to list what is still open. Read each answer in full.
3. Act on them. Under each used answer, add a line `→ Settled: <where it was recorded>` in the
   repository file (e.g. `docs/decisions.md` "<entry title>", `tasks/todo.md` <section>), then
   `push`. An answer that raises a new question gets a new ID, not an edit to the old one.
4. Record durable choices with the `update-decisions` workflow. A decision entry may cite the
   answers instead of restating them ("answers Q1–Q6 in `tasks/questions/<topic>.md`"), but state
   the decision itself in the entry.
5. Commit the questions file by explicit path with the work it informed.

## Edge cases

- `push` refuses when the review copy holds answers the file lacks: `pull`, then `push`.
- An editor may re-escape Markdown (`\_`, trailing `\`); `pull` ignores formatting-only
  differences. If `pull` finds nothing although the user says they answered, read the review copy
  and its comments directly; if the answers are not on disk, ask the user where they wrote them.
- `pull` reports IDs in the review copy that the file lacks: the user added a question; copy it in.
- The user may write edits into a question's own text ("changes written above"). `pull` copies only
  answers and `push` rewrites question text, so before each `push` diff the review copy against the
  file and carry such edits into the `→ Settled:` note.
