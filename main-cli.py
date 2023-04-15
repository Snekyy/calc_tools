#!/usr/bin/python3
from translate import interpret, interpret_reverse


def main():
	new_expr = []
	while True:
		tmp_expr = input("Enter next FunctionExpression: ")
		if tmp_expr == "":
			break
		new_expr.append(tmp_expr)
	math_expr = interpret(new_expr)
	math_expr: MathExpression
	diff_var = input("Enter a variable of differentiation: ")
	math_expr.differentiate(diff_var)
	print("Derivative is: ", interpret_reverse(math_expr))
	args = {}
	for var in math_expr.variables:
		args[var] = float(input(f"Enter value of the {var} variable: "))
	print("Derivative's value is: ", math_expr.value(args))


main()
