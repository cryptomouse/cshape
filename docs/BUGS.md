# Known Bugs

Started 2026-09-12, following the convention of Modest's `docs/BUGS.md`.

This file is the only place bugs are recorded, so a bug is referred to as
`BUG#N` everywhere — docs, source comments, test names, commit messages —
without naming the file.  The number is permanent: an entry is deleted when
the bug is fixed, and numbers are never reused.

Nothing is kept here about fixed bugs.  What survives a fix is the test that
reproduced it, renamed from `test_bugN_...` (expected to fail while the entry
is here) to a plain regression test with a `# Guards BUG#N (fixed <date>)`
comment.  Who fixed it and when is git's to answer:
`git log -S '## BUG#N:' -- docs/BUGS.md`.

## BUG#1: `CTypeArray` overwrites the item type's qualifiers

```python
CTypeArray(CTypeIdentifier("Point", ["const"]))
```

Renders `Point []` — the `const` is gone.  The constructor
(`cshape.py:197`) does `item_type.specifiers = specifiers` before anything
else, and `specifiers` defaults to `[]`, so whatever the item type carried is
replaced by nothing.  Only `CTypeArray(CTypeIdentifier("Point"),
specifiers=["const"])` works, which is how the README example is written.

- The assignment also mutates the node it was handed: a `CTypeIdentifier`
  shared between an array and a plain variable loses its qualifiers for the
  variable too, and the README encourages sharing (`i32 = CTypeIdentifier(...)`
  used in several places).
- The default `specifiers=[]` is a shared mutable list across every
  `CTypeArray` built without one; nothing appends to it today, so it is
  latent.
- The comment on that line ("array specs is array item specs (!)") says the
  intent: qualifiers on an array apply to its elements in C, so
  `CTypeArray(..., specifiers=[...])` has to reach the item type.  The fix is
  to merge rather than replace — copy the item type's list and extend it,
  or only assign when `specifiers` was actually given.
- Coverage: none yet.

## BUG#2: `.note` on values is documented but does not exist

`README.md` ("What it covers") and `docs/quickstart.md` ("Core Conventions")
describe a `.note` field on every value, printed as a `/* note */` comment
after the value, outside any parentheses added for precedence:

```c
3.125 /* totalVolume / elementVolume */
```

`cshape.py` has no such field: `CValue.__init__` sets only `mark` and `nl`,
and `str_cvalue` prints only `mark`.  Setting `v.note = "..."` is silently
accepted (it is a plain attribute) and never printed.  The docs arrived in
commit `c85acd3` without the code.

- Either implement it in `str_cvalue` — after `wrap_if`, so it lands outside
  the parentheses as documented — or drop the two paragraphs.  Implementing
  seems the intent: `mark` goes before a node and says *who* produced it,
  `note` goes after a value and says *what* it was before folding.
- Coverage: none yet.
