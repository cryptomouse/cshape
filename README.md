# cshape

A dependency-free C AST + printer for Python: build a tree and get C11
source back. No parsing, no dependencies beyond the standard library —
just `CType*` / `CValue*` / `CStmt*` nodes and a `render()` function that
turns them into text.

Originally the C backend's printer for the Modest compiler, split out
because it doesn't know anything about Modest — it only knows about C.

## Install

```sh
pip install cshape
```

## Example

A typedef'd struct, a function that walks an array of them, and a `.mark`
on one statement to show where it came from:

```python
from cshape import *

i32 = CTypeIdentifier("int32_t")
pts, n, i, acc = (CValueIdentifier(x) for x in ("pts", "n", "i", "acc"))
pt_x = CValueFieldAccess(CValueIndex(pts, i), "x")

point = CStmtDefType(
	id="Point",
	type=CTypeStruct(tag="struct", fields=[
		CField(id="x", type=i32, nl=1),
		CField(id="y", type=i32, nl=1),
	]),
)

skip_negative = CStmtIf(
	condition=CValueGE(pt_x, CValueInteger(0)),
	then_block=CStmtBlock([CStmtAssignment(acc, CValueAdd(acc, pt_x))]),
	else_block=None,
)
skip_negative.mark = "gen:filter"

sum_x = CStmtDefFunc(
	id="sum_x",
	type=CTypeFunction(
		params=[CField(id="pts", type=CTypePointer(CTypeIdentifier("Point", ["const"]))),
		        CField(id="n", type=CTypeIdentifier("int"))],
		to=i32,
	),
	block=CStmtBlock([
		CStmtDefVar(id="acc", type=i32, initializer=CValueInteger(0)),
		CStmtDefVar(id="i", type=CTypeIdentifier("int"), initializer=CValueInteger(0)),
		CStmtWhile(
			condition=CValueLt(i, n),
			block=CStmtBlock([skip_negative, CStmtIncrement(i)]),
		),
		CStmtReturn(acc),
	]),
)

unit = [CInclude("stdint.h", True), point, sum_x]
print("\n\n".join(render(node).strip() for node in unit))
```

Generated C:

```c
#include <stdint.h>

typedef struct {
	int32_t x;
	int32_t y;
} Point;

int32_t sum_x(const Point *pts, int n) {
	int32_t acc = 0;
	int i = 0;
	while (i < n) {
		/*gen:filter*/if (pts[i].x >= 0) {
			acc = acc + pts[i].x;
		}
		++i;
	}
	return acc;
}
```

(`render()` returns the node's own leading blank lines too — `CStmtDefFunc`
starts with a blank line by default, so `.strip()` if you're printing a
single node standalone rather than concatenating several.)

## Documentation

- [docs/api.md](docs/api.md) - documentation index
- [docs/quickstart.md](docs/quickstart.md) - getting started and first example
- [docs/reference.md](docs/reference.md) - current API reference

## What it covers

- Types: named types, pointers, arrays, function types, structs/unions, enums
- Values: the full C11 expression grammar with correct operator precedence
  and parenthesization (including the extra parens GCC/Clang warn about for
  mixed bitwise/shift expressions)
- Statements: blocks, if/while, return, break/continue, inline asm, raw
  inserts
- Preprocessor: `#define`, `#undef`, `#include`, `#if`/`#elif`/`#else`/`#endif`
  regions
- Two brace styles (`legacy` — K&R-ish, `modern` — Allman-ish), configurable
  via `render(node, style=...)`
- A `.mark` field on every node: set it to any string and it shows up as a
  `/*mark*/` comment right before that node in the output — useful for
  tracing which part of your own compiler/generator produced which bit of C
- A `.note` field on every value, printed as a `/* note */` comment *after*
  the value — for saying where a value came from once it no longer shows:
  `3.125 /* totalVolume / elementVolume */`

## What it doesn't do

No parsing, no semantic analysis, no type checking. It's a printer, not a
compiler frontend — you build the tree, it hands you back text.

## License

MIT
