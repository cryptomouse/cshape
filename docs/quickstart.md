# cshape Quickstart

`cshape` is a small dependency-free C AST builder and printer for Python.

You construct nodes from three main families:

- `CType*` for C types
- `CValue*` for expressions and literals
- `CStmt*` for statements and definitions

Then render them with `render(node, ...)`.

## Install

```sh
pip install cshape
```

## First Example

```python
from cshape import *

func = CStmtDefFunc(
	id="add",
	type=CTypeFunction(
		params=[
			CField(id="a", type=CTypeIdentifier("int")),
			CField(id="b", type=CTypeIdentifier("int")),
		],
		to=CTypeIdentifier("int"),
	),
	block=CStmtBlock([
		CStmtReturn(
			CValueAdd(
				CValueIdentifier("a"),
				CValueIdentifier("b"),
			)
		),
	]),
)

print(render(func).strip())
```

Output:

```c
int add(int a, int b) {
	return a + b;
}
```

## Rendering

```python
render(node, style='legacy', indent='\t', newline='\n')
```

- `node` can be a type node, value node, statement node, or top-level preprocessor node.
- `style` can be `legacy` or `modern`.
- `indent` controls one indentation unit.
- `newline` controls the newline sequence.

`render()` preserves mark comments and operator precedence handling. Some statement and definition nodes intentionally include their own leading blank lines, so `.strip()` is often convenient when rendering a single node standalone.

## Core Conventions

- Most nodes expose a `.mark` field. If set, it is emitted as a `/*mark*/` comment before that node.
- Values additionally expose a `.note` field, emitted as a `/* note */` comment after the value — and outside any parentheses precedence added, so it reads as a remark about the whole expression.
- `id` is used for C identifiers.
- `specifiers` is used for qualifiers and similar modifier tokens.
- `CStmtBlock` owns a list of nested statement nodes.

## What It Covers

- Types: named types, pointers, arrays, function types, structs/unions, enums
- Values: C11 expression nodes with precedence-aware printing
- Statements: blocks, if/while, return, break/continue, inline asm, raw text
- Preprocessor: `#define`, `#undef`, `#include`, and conditional regions
- Two brace styles through `render(node, style=...)`

## What It Does Not Do

- No parsing
- No semantic analysis
- No type checking

It is a printer, not a frontend. You build the tree yourself, and `cshape` turns it into C source text.

## Next Step

For exact constructor signatures and the full current API, see [reference.md](reference.md).