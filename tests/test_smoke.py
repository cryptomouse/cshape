import unittest

from cshape import (
	CField, CStmtBlock, CStmtDefFunc, CStmtDefVar, CStmtReturn, CTypeArray,
	CTypeFunction, CTypeIdentifier, CTypeStruct, CValueAdd, CValueArray,
	CValueIdentifier, CValueInteger, render,
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


if __name__ == '__main__':
	unittest.main()
