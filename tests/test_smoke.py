import unittest
from types import SimpleNamespace

from cshape import (
	CField, CStmtBlock, CStmtCompoundAssignment, CStmtDefFunc, CStmtDefVar,
	CStmtReturn, CTypeArray, CTypeFunction, CTypeIdentifier, CTypeStruct,
	CValueAdd, CValueArray, CValueIdentifier, CValueIndex, CValueInteger,
	CValueMul, render,
)


class SmokeTest(unittest.TestCase):
	def test_render_function(self):
		func = CStmtDefFunc(
			id='add',
			type=CTypeFunction(
				params=[CField(id='a', type=CTypeIdentifier('int')),
				        CField(id='b', type=CTypeIdentifier('int'))],
				to=CTypeIdentifier('int'),
			),
			block=CStmtBlock([
				CStmtReturn(CValueAdd(CValueIdentifier('a'), CValueIdentifier('b'))),
			]),
		)

		self.assertEqual(
			render(func).strip(),
			'int add(int a, int b) {\n\treturn a + b;\n}',
		)

	def test_render_is_reentrant(self):
		# render() must not leak indent/style state between independent calls
		named = CTypeIdentifier('int')
		render(named, style='modern')
		self.assertEqual(render(named, style='legacy'), 'int')

	def test_mark_shows_up_as_comment(self):
		v = CValueIdentifier('x')
		v.mark = 'debug-note'
		self.assertIn('/*debug-note*/', render(v))

	def test_value_constructor_accepts_nl_for_array_layout(self):
		array_def = CStmtDefVar(
			id='numbers',
			type=CTypeArray(CTypeIdentifier('int')),
			initializer=CValueArray([
				CValueInteger(1, nl=1),
				CValueInteger(2),
			]),
		)

		self.assertEqual(
			render(array_def).strip(),
			'int numbers[] = {\n\t1, 2\n};',
		)

	def test_struct_attributes_follow_the_closing_brace(self):
		# a struct attribute is only read after the body: before the
		# declaration the compiler ignores it
		packed = CStmtDefVar(
			id='',
			type=CTypeStruct(
				fields=[CField(id='tag', type=CTypeIdentifier('uint8_t')),
				        CField(id='len', type=CTypeIdentifier('uint32_t'))],
				tag='struct header',
				attributes={'packed': {}},
			),
		)

		self.assertEqual(
			render(packed).strip(),
			'struct header {uint8_t tag; uint32_t len;} __attribute__((packed));',
		)

	def test_compound_assignment(self):
		x = CValueIdentifier('x')
		self.assertEqual(
			render(CStmtCompoundAssignment(x, '+=', CValueInteger(1))).strip(),
			'x += 1;',
		)
		# the right side is a whole expression: no parentheses needed
		a_i = CValueIndex(CValueIdentifier('a'), CValueIdentifier('i'))
		rhs = CValueAdd(CValueIdentifier('y'), CValueMul(x, CValueInteger(2)))
		self.assertEqual(
			render(CStmtCompoundAssignment(a_i, '<<=', rhs)).strip(),
			'a[i] <<= y + x * 2;',
		)
		with self.assertRaises(AssertionError):
			CStmtCompoundAssignment(x, '=', CValueInteger(1))

	def test_array_qualifiers_go_to_leaf_item(self):
		# C11 6.7.3p9: an array's qualifiers are its items' qualifiers;
		# they add to the item's own and reach the innermost item
		own = CTypeArray(CTypeIdentifier('int', specifiers=['volatile']), CValueInteger(4))
		self.assertEqual(render(CStmtDefVar('a', own)).strip(), 'volatile int a[4];')

		inner = CTypeArray(CTypeIdentifier('int'), CValueInteger(2))
		grid = CTypeArray(inner, CValueInteger(2), specifiers=['volatile'])
		self.assertEqual(render(CStmtDefVar('g', grid)).strip(), 'volatile int g[2][2];')

		grid.specifiers.remove('volatile')
		self.assertEqual(render(CStmtDefVar('g', grid)).strip(), 'int g[2][2];')

	def test_attribute_keeps_indent_inside_block(self):
		# the declaration after an attribute keeps the block's indent;
		# at the top level nothing changes
		x = CStmtDefVar('x', CTypeIdentifier('int'), initializer=CValueInteger(1),
		                attributes={'alignment': SimpleNamespace(asset=16)})
		self.assertEqual(render(x).strip(), '__attribute__((aligned(16)))\nint x = 1;')
		self.assertEqual(
			render(CStmtBlock([x])),
			'{\n\t__attribute__((aligned(16)))\n\tint x = 1;\n}',
		)


if __name__ == '__main__':
	unittest.main()
