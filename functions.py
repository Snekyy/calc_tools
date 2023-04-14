from itertools import product
from copy import deepcopy
from typing import Union, Callable, Optional


class Monomial:
	def __init__(self, factors: dict[str, int], const: float = 1.0, variables: Optional[set] = None):
		"""
		# A model of a monomial (product of many variables).
		:param factors: A dict of factors names (i.e. variables letters) E.g.: {"x": degree_x, "y": degree_y, ...}
		:param const: is a K in k*x^2*y^8*z^3, i.e. multipier.
		:param variables: the variables degrees. E.g. {"x", "y", ...}
		"""
		self.factors = factors
		self.const = const
		if variables is None:
			self.variables: set = self._count_vars()
		else:
			self.variables: set = variables

	def monomial_value(self, args: dict) -> float:
		my_product = self.const
		for key in args:
			if key in self.variables:
				my_product *= (args[key] ** self.factors[key])
		return my_product

	# returns a list of variables used in monomial
	def _count_vars(self):
		return {var_i for var_i in self.factors.keys()}


# A model of a polynom (sum of monomials);
# A list of monomials.
class Polynom:
	def __init__(self, monomials):
		self.monomials: list[Monomial] = monomials
		self.variables: set = set()
		for monomial in monomials:
			self.variables |= monomial.variables

	# Приводит подобные слагаемые
	def simplify(self):
		m_factors = [m_i.factors for m_i in self.monomials]
		pre_monomials = {}
		for i, m in enumerate(m_factors):
			dict_str = str(m)
			if dict_str in pre_monomials:
				pre_monomials[dict_str].append(i)
			else:
				pre_monomials[dict_str] = [i]
		monomials = []
		for similar_monomials_i in pre_monomials.values():
			factors = m_factors[similar_monomials_i[0]]
			const = sum([self.monomials[i].const for i in similar_monomials_i])
			monomials.append(Monomial(factors, const))
		self.monomials = monomials

	# Возводит полином в квадрат
	def square(self):
		new_poly = Product(self, self).multiply()
		new_poly.simplify()
		return new_poly

	def polinom_value(self, my_dict: dict[str, float]) -> float:
		return sum([monomial.monomial_value(my_dict) for monomial in self.monomials])


class FunctionExpression:

	def __init__(self, polynom1: Polynom, polynom2: Polynom):
		"""
		A model of a rational function (fraction):
		:param polynom1: as dividend;
		:param polynom2: as divisor.
		"""
		self.dividend: Polynom = polynom1
		self.divisor: Polynom = polynom2

		self.variables: set = self.dividend.variables | self.divisor.variables
		# print(f'dividend"s vars: {self.dividend.variables}', f'divisor"s vars: {self.divisor.variables}')
		# print(f'func"s vars: {self.variables}')

	def function_expression_value(self, my_dict: dict) -> float:
		return self.dividend.polinom_value(my_dict) / self.divisor.polinom_value(my_dict)


class MathExpression:
	def __init__(self, expression: list, var: str):
		"""A model of sum of rational functions of many variables."""
		self.expressions: list[FunctionExpression] = expression
		self.var = var

		self.variables: set = set()
		for expr in self.expressions:
			self.variables |= expr.variables

	def differentiate(self):
		total_derivative = []
		for func_expr in self.expressions:
			total_derivative.append(Derivative(func_expr, self.var)._find())
		self.expressions = total_derivative
		# return MathExpression(total_derivative, self.var)

	def math_expression_value(self, my_dict: dict) -> float:
		"""
		:param my_dict: len(self.variables == len(my_dict) is True
		:return: sum of value FuncExpressions
		"""
		return sum([expression.function_expression_value(my_dict) for expression in self.expressions])


# A model of a product of polynoms\monomials
# Main method is a "multiply":
# 1) перемножает два полинома, раскрывая скобки
# и упрощая выражение приведением подобных слагаемых в случае полиномов;
# 2) перемножает два монома и упрощает выражение, объединяя под
# одну степень одинаковые множители (переменные) в случае мономов;
class Product:
	# factor1, factor2 are Polynoms both or monomils both
	def __init__(self, factor1: Union[Polynom, Monomial], factor2: Union[Polynom, Monomial]):
		assert type(factor1) == type(factor2)
		self.factor1: Union[Polynom, Monomial] = factor1
		self.factor2: type(factor1) = factor2

	def multiply_monomials(self) -> Monomial:
		res_const = self.factor1.const * self.factor2.const
		res_variables = self.factor1.variables | self.factor2.variables
		res_factors = {}
		for var_i in res_variables:
			res_factors[var_i] = self.factor1.factors.get(var_i, 0) + self.factor2.factors.get(var_i, 0)
		return Monomial(res_factors, res_const, res_variables)

	def multiply_polynoms(self) -> Polynom:
		# a list of monomials
		monomials = []
		for monomial_1, monomial_2 in product(self.factor1.monomials, self.factor2.monomials):
			monomials.append(Product(monomial_1, monomial_2).multiply())
		res = Polynom(monomials)
		res.simplify()
		return res

	def multiply(self) -> Union[Polynom, Monomial]:
		if isinstance(self.factor1, Polynom):
			return self.multiply_polynoms()
		else:
			return self.multiply_monomials()


class Derivative(FunctionExpression):
	"""
	Этот класс создан, чтобы находить производную для FunctionExpression
	Его основной метод - find - возвращает объект типа FunctionExpression, который
	и является производной входного FunctionExpression.
	"""
	def __init__(self, function: FunctionExpression, var: str):
		super().__init__(function.dividend, function.divisor)
		# Переменная дифференцирования, a string. I.e. "x".
		# Т.о, выделяется пер. дифф. среди всех переменных в полиноме
		self.var: str = var
		self.derivative: FunctionExpression = self._find()

	def _differentiate_monomial(self, monomial: Monomial) -> Monomial:
		if self.var not in monomial.factors or monomial.factors[self.var] == 0:
			return Monomial({self.var: 0}, 0)  # just a 0
		else:
			const = monomial.const * monomial.factors[self.var]
			factors = deepcopy(monomial.factors)
			factors[self.var] -= 1
			return Monomial(factors, const)

	def _differentiate_polynom(self, polynom: Polynom) -> Polynom:
		res_poly_monomials = []
		for monom in polynom.monomials:
			# print(f'monom"s  {monom.__dict__}')
			res_poly_monomials.append(self._differentiate_monomial(monom))
		return Polynom(res_poly_monomials)

	# is a derivative of a origin function
	def _find(self) -> FunctionExpression:
		# prepare a list of monomials
		if self.var in self.divisor.variables:
			pre_dividend = []
			pre_dividend += Product(self._differentiate_polynom(self.dividend), self.divisor).multiply_polynoms().monomials
			pre_dividend += Product(Product(self.dividend, self._differentiate_polynom(self.divisor)).multiply_polynoms(), Polynom([Monomial({self.var: 0}, -1)])).multiply_polynoms().monomials
			dividend = Polynom(pre_dividend)
			dividend.simplify()
			divisor = self.divisor.square()
		else:
			divisor = self.divisor
			dividend = self._differentiate_polynom(self.dividend)
		return FunctionExpression(dividend, divisor)
