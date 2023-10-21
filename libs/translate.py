from .functions import *


def _str_to_monomial(monomial_str: str) -> Monomial:
	""" Translates monomial expression in string format to Monomial object
	
		:param monomial_str: string, presenting monomial expression
			e.g. "3*x^5*y^3*z^2"
	"""
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
	""" Translates polynomial expression in string format to Polynomial object
	
		:param polynomial_str: string, presenting polynomial expression
			e.g. "3*x^5*y^3*z^2 + 2*x^2"
	"""
	monomials = [_str_to_monomial(monomial_str) for monomial_str in polynomial_str.split(" + ")]
	return Polynomial(monomials)


def interpret(expression_str: list[str]) -> MathExpression:
	""" Translates math expression in string format to MathExpression object
	
		:param expression_str: string, presenting math expression
			e.g. "3*x^5*y^3*z^2 + 2*x^2/x^5 + x^2/y^5"
	"""
	math_expr = []
	for func_expr in expression_str:
		if "/" in func_expr:
			dividend, divisor = func_expr.split("/")
			divisor: str
			divisor = _str_to_polynomial(divisor)
		else:
			dividend = func_expr
			divisor: Polynomial = Polynomial.one()
		dividend = _str_to_polynomial(dividend)
		math_expr.append(RationalFunction(dividend, divisor))
	return MathExpression(math_expr)


def _monomial_to_str(monomial: Monomial) -> str:
	""" Takes Monomial object and returns its expression in string format 
	
		:param monomial: a monomial object, which is going to be used for translation
	"""
	if monomial.factors == Monomial.zero().factors:
		return str(monomial.const)
	else:
		monomial_ls = []
		monomial_ls.append(str(monomial.const))
		for factor, degree in monomial.factors.items():
			monomial_ls.append(str(factor) + "^" + str(degree))
		return "*".join(monomial_ls)


def _polynomial_to_str(polynomial: Polynomial) -> str:
	""" Takes Polynomila object and returns its expression in string format 
	
		:param polynomial: a polynomial object, which is going to be used for translation
	"""
	polynomial_ls = []
	for monomial in polynomial.monomials:
		monomial_str = _monomial_to_str(monomial)
		if not monomial_str == "0":
			polynomial_ls.append(monomial_str)
	if len(polynomial_ls) == 0:
		return "0"
	return " + ".join(polynomial_ls)


def _rational_function_to_str(func_expr: RationalFunction) -> str:
	""" Takes RationalFunction object and returns its expression in string format 
	
		:param func_expr: a polynomial object, which is going to be used for translation
	"""
	dividend = _polynomial_to_str(func_expr.dividend)
	divisor = _polynomial_to_str(func_expr.divisor)
	if divisor == "1":
		return dividend
	else:
		return "("+dividend+")/("+divisor+")"


def interpret_reverse(math_expr: MathExpression) -> str:
	""" Takes MathExpression object and returns its expression in string format 
	
		:param math_expr: a polynomial object, which is going to be used for translation
	"""
	math_expr_str = []
	for func_expr in math_expr.expression:
		math_expr_str.append(_rational_function_to_str(func_expr))
	return " + ".join(math_expr_str)

