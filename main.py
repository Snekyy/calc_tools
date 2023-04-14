#!/usr/bin/python3
from functions import *


def interprete_reverse(math_expression: MathExpression) -> str:
	"""translates from MathExpression to string"""
	func_strings = []
	for func_expression in math_expression.expressions:
		polynoms_strings = []
		for polynom in (func_expression.dividend, func_expression.divisor):
			monomials_strings = []
			for monomial in polynom.monomials:
				if monomial.const == 0:
					continue
				factors_str = "*".join([f'{key_var}^{monomial.factors[key_var]}' for key_var in monomial.factors])
				monomial_str = f"{monomial.const}*{factors_str}"
				monomials_strings.append(monomial_str)
			polynoms_strings.append(" + ".join(monomials_strings))
		res_poly_string = "/".join(polynoms_strings)
		func_strings.append(res_poly_string)
	print("The derivative is: ", " + ".join(func_strings))
	#return deriv_expr


def interprete(expression: str) -> FunctionExpression:
	"""translates from string to FunctionExpression, Polynom and Monomial"""
	if "/" not in expression:
		dividend = expression
		polynom_2: Polynom = Polynom([Monomial({"F": 0})])
	else:
		dividend, divisor = expression.split("/")
		polynom_2 = expression_to_polynom(divisor)
	polynom_1 = expression_to_polynom(dividend)
	func_expression = FunctionExpression(polynom_1, polynom_2)
	return func_expression


def expression_to_polynom(expression: str) -> Polynom:
	"""
	Expression to polynom
	1. str -  3*x^5 + y^7
	2. list[str] - [3*x^5, y^7]
	3. list[list[str]] - [[3, x^5], [y^7]]
	4. list[list[list[str]]] - [[[3], [x, 5]], [[y, 7]]]
	"""
	expression: list = expression.split(" + ")
	for index_1, small_expression_1 in enumerate(expression):
		expression: list[str]
		expression[index_1] = small_expression_1.split("*")
		for index_2, small_expression_2 in enumerate(expression[index_1]):
			expression: list[list[str]]
			expression[index_1][index_2] = small_expression_2.split("^")
	expression: list[list[list[str]]]
	monomials = [list_to_monomial(primary_lists) for primary_lists in expression]
	return Polynom(monomials)


def list_to_monomial(monomial_list: list) -> Monomial:
	const = 1.0
	factors_args = {}
	got_minus = False
	for arg in monomial_list:
		if len(arg) == 1:
			const = float(arg[0])
		elif len(arg) == 2:
			var, degree = (arg[0], arg[1]) if not arg[0].isdigit() else (arg[1], arg[0])
			degree = int(degree)
			if var.startswith('-'):
				var = var[1:]
				got_minus = True
			factors_args[var] = degree
	if not factors_args:
		factors_args = {"F": 0}
	if got_minus:
		const *= -1
	return Monomial(factors_args, const)


def main():
	new_expr = []
	while True:
		# There're a strict syntax of a FunctionExpression formula input
		tmp_expr = input("Enter next FunctionExpression: ")  # 2*x^3 + x^1*y^7*z^2/3*x^5 + y^7
		if tmp_expr == "":
	 		break
		new_expr.append(interprete(tmp_expr))
	derivs = {}
	koefs = {"A": 0.0029, "B": 0.0015, "C": 6.3, "D": 1.82, "F": 1}
	pogreshn = {"A": 0.0002, "B": 0.0005, "C": 0.6, "D": 0.5}
	for var_i in ("A", "B", "C", "D", "T1"):
		function = MathExpression(new_expr, var_i)
		function.differentiate()
		derivs[var_i] = function
		interprete_reverse(function); print(var_i)
	pogr = []
	for key in pogreshn.keys():
		pogr.append(derivs[key].math_expression_value(koefs)*pogreshn[key])
	print([(derivs[key].math_expression_value(koefs), key) for key in pogreshn.keys()])
	print("total pogr is", sum([pogr_i**2 for pogr_i in pogr]))


if __name__ == "__main__":
	main()
