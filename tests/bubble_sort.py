import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cshape import (
    CStmtLineComment,
	CInclude,
	CMacroDef,
	CField,
	CStmtExpr,
	CStmtAssignment,
	CStmtBlock,
	CStmtDefFunc,
	CStmtDefVar,
	CStmtIf,
	CStmtIncrement,
	CStmtReturn,
	CStmtWhile,
	CTypeArray,
	CTypeFunction,
	CTypeIdentifier,
	CTypePointer,
	CValueAdd,
	CValueArray,
	CValueCall,
	CValueGt,
	CValueIdentifier,
	CValueIndex,
	CValueInteger,
	CValueLt,
	CValueSub,
	CValueString,
	render,
)


def build_bubble_sort():
	arr = CValueIdentifier('arr')
	i = CValueIdentifier('i')
	j = CValueIdentifier('j')
	n = CValueIdentifier('n')
	temp = CValueIdentifier('temp')

	arr_j = CValueIndex(arr, j)
	arr_j_next = CValueIndex(arr, CValueAdd(j, CValueInteger(1)))

	return CStmtDefFunc(
		id='bubble_sort',
		type=CTypeFunction(
			params=[
				CField(id='arr', type=CTypePointer(CTypeIdentifier('int'))),
				CField(id='n', type=CTypeIdentifier('int')),
			],
			to=CTypeIdentifier('void'),
		),
		block=CStmtBlock([
			CStmtDefVar(id='i', type=CTypeIdentifier('int'), initializer=CValueInteger(0)),
			CStmtDefVar(id='j', type=CTypeIdentifier('int'), initializer=CValueInteger(0)),
			CStmtDefVar(id='temp', type=CTypeIdentifier('int')),
			CStmtWhile(
				condition=CValueLt(i, CValueSub(n, CValueInteger(1))),
				block=CStmtBlock([
					CStmtAssignment(j, CValueInteger(0)),
					CStmtWhile(
						condition=CValueLt(j, CValueSub(CValueSub(n, i), CValueInteger(1))),
						block=CStmtBlock([
							CStmtIf(
								condition=CValueGt(arr_j, arr_j_next),
								then_block=CStmtBlock([
									CStmtAssignment(temp, arr_j),
									CStmtAssignment(arr_j, arr_j_next),
									CStmtAssignment(arr_j_next, temp),
								]),
								else_block=None,
							),
							CStmtIncrement(j),
						]),
					),
					CStmtIncrement(i),
				]),
			),
		]),
	)


def build_program():
	array_size = CValueIdentifier('ARRAY_SIZE')
	numbers = CValueIdentifier('numbers')
	i = CValueIdentifier('i')

	global_array = CStmtDefVar(
		id='numbers',
		type=CTypeArray(CTypeIdentifier('int'), size=array_size),
		initializer=CValueArray([
			CValueInteger(64, nl=1),
			CValueInteger(34),
			CValueInteger(25),
			CValueInteger(12),
			CValueInteger(22),
			CValueInteger(11),
			CValueInteger(90),
		]),
	)

	main_func = CStmtDefFunc(
		id='main',
		type=CTypeFunction(params=[], to=CTypeIdentifier('int')),
		block=CStmtBlock([
			CStmtDefVar(id='i', type=CTypeIdentifier('int'), initializer=CValueInteger(0)),
			CStmtExpr(CValueCall(CValueIdentifier('bubble_sort'), [numbers, array_size])),
			CStmtWhile(
				condition=CValueLt(i, array_size),
				block=CStmtBlock([
					CStmtExpr(CValueCall(CValueIdentifier('printf'), [
						CValueString('%d ', 8),
						CValueIndex(numbers, i),
					])),
					CStmtIncrement(i),
				]),
			),
			CStmtExpr(CValueCall(CValueIdentifier('printf'), [CValueString('\\n', 8)])),
			CStmtReturn(CValueInteger(0)),
		]),
	)

	return [
        CStmtLineComment([
            ' Bubble sort implementation',
            ' Just example'
        ]),
		CInclude('stdio.h', True),
		CMacroDef('ARRAY_SIZE', '7'),
		global_array,
		build_bubble_sort(),
		main_func,
	]


def render_program(definitions):
	return '\n\n'.join(render(definition).strip() for definition in definitions)


if __name__ == '__main__':
	print(render_program(build_program()))

