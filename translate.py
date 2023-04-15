from functions import *


def _str_to_monomial(monomial_str: str) -> Monomial:
	monomial_ls = [factor_str.split("^") for factor_str in monomial_str.split("*")]
	const = 1.0
	factors = {}
	for elem in monomial_ls:
		if len(elem) == 1:
			const = float(elem[0])
		elif len(elem) == 2:
			var, degree = elem[0], elem[1]
			degree = int(degree)
			if var.startswith('-'):
				var = var[1:]
				const *= -1
			factors[var] = degree
	return Monomial(factors, const)


def _str_to_polynomial(polynomial_str: str) -> Polynomial:
	"""
	String to polynomial object.
	1. str -  3*x^5 + y^7
	2. list[str] - [3*x^5, y^7]
	3. list[list[str]] - [[3, x^5], [y^7]]
	4. list[list[list[str]]] - [[[3], [x, 5]], [[y, 7]]]
	"""
	monomials = [_str_to_monomial(monomial_str) for monomial_str in polynomial_str.split(" + ")]
	return Polynomial(monomials)


def interpret(expression: list[str]) -> MathExpression:
	""" Translates a list of strings to MathExpression object."""
	math_expr = []
	for func_expr in expression:
		if "/" in func_expr:
			dividend, divisor = func_expr.split("/")
			divisor: str
			divisor = _str_to_polynomial(divisor)
		else:
			dividend = func_expr
			divisor: Polynomial = Polynomial.one()
		dividend = _str_to_polynomial(dividend)
		math_expr.append(FunctionExpression(dividend, divisor))
	return MathExpression(math_expr)


def _monomial_to_str(monomial: Monomial) -> str:
	if monomial == Monomial.zero():
		return "0"
	elif monomial.factors == Monomial.zero().factors:
		return str(monomial.const)
	else:
		monomial_ls = []
		monomial_ls.append(str(monomial.const))
		for factor, degree in monomial.factors.items():
			monomial_ls.append(str(factor) + "^" + str(degree))
		return "*".join(monomial_ls)


def _polynomial_to_str(polynomial: Polynomial) -> str:
	polynomial_ls = []
	for monomial in polynomial.monomials:
		monomial_str = _monomial_to_str(monomial)
		if not monomial_str == "0":
			polynomial_ls.append(monomial_str)
	if len(polynomial_ls) == 0:
		return "0"
	return " + ".join(polynomial_ls)


def _function_expression_to_str(func_expr: FunctionExpression) -> str:
	dividend = _polynomial_to_str(func_expr.dividend)
	divisor = _polynomial_to_str(func_expr.divisor)
	if divisor == "1":
		return dividend
	else:
		return "("+dividend+")/("+divisor+")"


def interpret_reverse(math_expr: MathExpression) -> str:
	""" Translates from MathExpression object to string."""
	math_expr_str = []
	for func_expr in math_expr.expression:
		math_expr_str.append(_function_expression_to_str(func_expr))
	return " + ".join(math_expr_str)

