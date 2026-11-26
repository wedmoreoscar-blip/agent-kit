# Verification

Report `PASS`, `FAIL`, `SKIP`, and `BLOCKED` distinctly. State the exact command, relevant output, and
coverage boundary.

## Profiles

Run the project wrapper from the repository root:

```bash
tools/test-project related     # only the tests the files you changed can affect
tools/test-project quick
tools/test-project build
tools/test-project full        # the gate; a clean run is recorded for its commit
tools/test-project recorded    # the recorded full run for main, if main has not moved since
```

The profiles and the commands behind them are defined in the `[profiles]` and `[commands]` blocks of
`docs/project_profile.md`, so this file never needs to name a project's tooling. While working, run
`related`. Before committing, use the smallest profile that covers the change. The whole suite and
the `full` profile are the gate at integration, run once per wave, not a habit after every edit. Do
not silently redefine build success as test success.

**`related` selects by imports, and has the blind spots that implies.** It runs the tests whose
import graph reaches the changed files. A test that opens a source file with a file read imports
nothing, so it is never selected; that is one more reason such checks are review evidence rather
than standing tests (`speccheck` step 5). A deleted file has no import graph either: typecheck and
the final baseline cover deletions. Configuration, fixtures and other non-code inputs may not be
traced at all; when a change is mostly those, run `quick`.

## Evidence categories

Static analysis (types, lint), bundle or build, unit and integration tests, browser behavior in a
running application, live backend behavior, and native-device behavior are distinct categories. The
project profile lists which of them exist here and which are `BLOCKED` for lack of infrastructure.

A change can pass one category and remain blocked in another. Report that boundary directly.
Missing infrastructure is `BLOCKED`, never `PASS`.

## A check is only evidence if it can fail

- **A green check is only evidence if the command has been shown to be capable of going red.**
  When adopting or trusting a verification command, prove it fails on a deliberate fault before
  treating its success as meaningful. A type check that compiles zero files exits 0 forever.
- **A known-failing check is not evidence either, and a fixed count invites everyone to stop reading
  it.** Baseline entries are for known, understood, individually named failures. A parse or syntax
  error is never baseline noise: it can hide a real defect inside an unchanged total, and it
  suppresses further analysis of that file. Read the failures, not only the count.
- **Where a file's only static check is one the baseline discounts, that file has no verification
  at all.** Know which checks cover which directories; a test runner that reads a file as text, or
  a type checker whose project config excludes a directory, does not check it.
- **Type checking and tests are not redundant.** Many test runners strip types without checking
  them, so a suite can pass straight over a type error.
- **Derive every count by running the command, never by quoting a document.** Recorded counts go
  stale the moment any change moves them.

## End-to-end checks, where applicable

Unit tests prove the pieces; a few end-to-end checks prove the product works. Each project lists its
critical flows under `## Critical flows` in `docs/project_profile.md`, three to five of them, with
one check each, run by `[commands].e2e`:

- **An app with a UI:** a browser test (Playwright) that drives the flow as a user would.
- **A pipeline, job or CLI with no UI:** one run of the real entry point on frozen fixture inputs,
  asserting on the output it produces, with network and paid services replaced by recorded
  responses. Driving it through a browser would test nothing it does.
- **A library:** an example that exercises the public API from end to end.

Not every project needs one, which is why this is "where applicable". A flow that needs
infrastructure agents cannot reach goes under `[implementer].blocked` and is reported `BLOCKED`.
Where it is runnable, `e2e` belongs in the `full` profile, so it runs once per wave at the final
baseline and never per leg. Keep the list short: an end-to-end check is the slowest and the most
likely to flake, so each must earn its place by covering a flow whose failure a user would notice.
Hundreds of narrow checks do not substitute for one that runs the product.

## High-risk areas

Each project lists its own high-risk areas, and the extra verification they need, under
`## High-risk areas` in `docs/project_profile.md`. Do not rely on typecheck alone for any of them.

## A crashed checkout can zero files that git still believes are committed

If the machine goes down seconds after a commit, merge or checkout, git may have written the ref
updates while file and object writes were still in the page cache. On restart the newest commit,
its trees and blobs can be 0-byte files (`fatal: bad object HEAD`), and working files just written
can be empty while the index still records them as committed and unmodified.

**Repair without rewriting a ref.** A git object's name is the hash of its content, so re-creating
lost objects byte-for-byte restores the same hashes and every ref pointing at them becomes valid
again. Back up `.git` first, then:

```bash
find .git/objects -type f -empty          # the damage, precisely
git fsck --no-dangling                    # what refs and trees depend on it
# rebuild the file content, then confirm it hashes to the missing blob BEFORE writing:
git hash-object <rebuilt-file>
rm .git/objects/<the empty files>
git hash-object -w <rebuilt-file>
GIT_INDEX_FILE=$tmp git read-tree <parent> && GIT_INDEX_FILE=$tmp git update-index --cacheinfo …
GIT_INDEX_FILE=$tmp git write-tree        # must equal the missing tree
GIT_AUTHOR_DATE=… GIT_COMMITTER_DATE=… git commit-tree <tree> -p <parent>   # must equal the missing commit
```

The author and committer dates come from the reflog, whose entries survive as text; the message must
be reproduced exactly, trailers included. If any hash does not match, stop: the content is not what
was committed, and moving the ref instead is the honest fallback.

**Restore working files only where the file is empty on disk and non-empty in `HEAD`.** Anything else
that differs is real uncommitted work, not crash damage, and a blanket `git checkout -f` or
`git restore .` would destroy it silently.

**Then re-run the full baseline rather than trusting the pre-crash result.** The tree that was
verified and the tree on disk were not the same bytes.
