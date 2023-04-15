from copy import deepcopy
from typing import Union
from itertools import product


class Monomial:

	def __eq__(self, other):
		if self.factors == other.factors and self.const == other.const:
			return True
		return False
	
	def __init__(self, factors: dict[str, int], const: float = 1.0):
		""" A model of a monomial (product of many variables).
		:param factors: A dict of factors names(i.e. variables letters);
			i.e.: {"x": degree_x, "y": degree_y, ...}.
			Factors may be an empty dict, then the monomial just a constant.
		:param const: is a K in k*x^2*y^8*z^3, i.e. multipier.
		"""
		self.factors = factors
		self.const = const
		# variables in monomial. E.g. {"x", "y", ...}
		self.variables: set = self.__count_variables()

	@staticmethod
	def zero():
		return Monomial({}, 0)

	@staticmethod
	def one():
		return Monomial({}, 1)

	def __count_variables(self) -> set:
		""" Returns a set of the monomial variables."""
		return set(self.factors.keys())

	def _cleanup(self) -> None:
		""" If the Monomial's const is a zero, changes the Monomials's 
		factors to a Monomial.zero().factors, i. e an empty dict.
		If the Monomial has zeros in factors.values(), i. e.
		variables in a monomials's product at a zero degrees,
		deletes that factors's.
		"""
		old_factors = self.factors
		if self.const == 0:
			new_factors = Monomial.zero().factors
		else:
			new_factors = {}
			for var, degree in old_factors.items():
				if degree != 0:
					new_factors[var] = degree
		self.factors = new_factors
		# Update Monomial's variables attr
		self.variables = self.__count_variables()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a monomial in (x, y, z, ...),
		where x, y, z = args["x"], args["y"], args["z"]
		"""
		value = self.const
		for key in args:
			if key in self.variables:
				value *= (args[key] ** self.factors[key])
		return value 


class Polynomial:
	def __init__(self, monomials: list[Monomial]):
		""" A model of a polynomial of many variables(sum of monomials).
		:param monomials: list of the monomials in polynomial.
		"""
		self.monomials = monomials
		self.variables: set = self.__count_variables()

	@staticmethod
	def one():
		return Polynomial([Monomial.one()])

	def __cleanup(self):
		""" Remove zero monomials from polynomial."""
		for monomial in self.monomials:
			monomial._cleanup()
			if monomial == Monomial.zero():
				self.monomials.remove(monomial)
		# if all monomials were zeros
		if len(self.monomials) == 0:
			self.monomials.append(Monomial.zero())
		self.variables = self.__count_variables()
	
	def __count_variables(self):
		""" Returns set of variables in polynomial(monomials)."""
		variables = set()
		for monomial in self.monomials:
			variables |= monomial.variables
		return variables

	def simplify(self) -> None:
		""" Combines like terms in polynomial and deletes
		zero monomials, i.e. Monomial.zero().
		"""
		# combines like terms(monomials)
		old_monomials = self.monomials
		new_monomials = []
		monomial_factors = [m_i.factors for m_i in old_monomials]
		monomial_counter = {}
		for i, factors in enumerate(monomial_factors):
			dict_key = str(factors)
			# like term
			if dict_key in monomial_counter:
				monomial_counter[dict_key].append(i)
			# new uniq term
			else:
				monomial_counter[dict_key] = [i]
		for like_monomials_i in monomial_counter.values():
			factors = monomial_factors[like_monomials_i[0]]
			const = sum([old_monomials[i].const for i in like_monomials_i])
			new_monomials.append(Monomial(factors, const))
		self.monomials = new_monomials
		# deleting zero monomials
		self.__cleanup()
		# updating variables list
		self.variables = self.__count_variables()

	def square(self) -> None:
		""" Squares a polynomial."""
		squared_polynomial = Product(self, self).multiply()
		self.monomials = squared_polynomial.monomials
		self.simplify()

	def minus(self):
		""" Returns polynomial mulitplied on a -1 for
			changing the sign of a polynomial.
		""" 
		minus_one_monomial = Monomial({}, -1)
		minus_one_polynomial = Polynomial([minus_one_monomial])
		self.monomials = Product(self, minus_one_polynomial).multiply().monomials

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a polynomial in (x, y, z, ...),
		where x, y, z = args["x"], args["y"], args["z"]
		"""
		return sum([monomial.value(args) for monomial in self.monomials])


class FunctionExpression:
	def __init__(self, poly_dividend: Polynomial, poly_divisor: Polynomial):
		""" A model of a rational function of many variables (fraction):
		:param poly_dividend: polynom in numerator(dividend);
		:param poly_divisor: polynom in denumerator(divisor).
		"""
		self.dividend: Polynomial = poly_dividend
		self.divisor: Polynomial = poly_divisor
		# Variables used in the rational function
		self.variables: set = self.__count_variables()

	def __count_variables(self):
		return self.dividend.variables | self.divisor.variables

	def simplify(self):
		""" Returns set of variables in MathExpression,
			i.e. in union of polynom-dividend variables and 
			polynom-divisor variables.
		"""
		self.dividend.simplify()
		self.divisor.simplify()
		self.variables = self.__count_variables()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a rational function in (x, y, z, ...),
		where x, y, z = args["x"], args["y"], args["z"]
		"""
		return self.dividend.value(args)/self.divisor.value(args)


class MathExpression:
	def __init__(self, expression: list[FunctionExpression]):
		""" A model of sum of rational functions of many variables.
		:param expression: a list of a FunctionExpresstions(i.e rational functions)
		"""
		self.expression: list[FunctionExpression] = expression
		self.simplify()
		# Variables used in a rational functions of that sum(MathExpression)
		self.variables: set = self.__count_variables()

	def __count_variables(self):
		""" Returns set of variables in union of all
			FunctionExpressions in self.expression, i.e. returns
			variables, which are used in the sum of rational functions."""
		variables = set()
		for func_expr in self.expression:
			variables = variables | func_expr.variables
		return variables
	
	def simplify(self):
		""" Runs simplify() to every FunctionExpression in self.expression.
		"""
		for func_expr in self.expression:
			func_expr.simplify()

	def differentiate(self, var: str) -> None:
		""" Differentiates "self" (MathExpression), i.e. finds
		derivatives of every FunctionExpression(rational function) in 
		that MathExpression(sum) and changes expression atr
		in that MathExpression
		:param var: A variable of a differentiation. E.g. var="x".
		"""
		derivative_expr = []
		for func_expr in self.expression:
			derivative_expr.append(Derivative(func_expr, var)._find())
		self.expression = derivative_expr
		self.simplify()
		self.variables = self.__count_variables()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a sum of FunctionExprestion's values in self.expression.
		:param args: len(self.variables == len(my_dict) is True
		:return: sum of value FuncExpressions
		"""
		return sum([func_expr.value(args) for func_expr in self.expression])


class Product:
	def __init__(self, factor1: Union[Polynomial, Monomial], factor2: Union[Polynomial, Monomial]):
		"""	A model of a product of Polynomials/Monomials.
		Main method of the class is "multiply".
		:param factor1: a polynom or a monomial which
		 is a factor in the product
		:param factor2: the same
		"""
		assert type(factor1) == type(factor2)
		self.factor1: Union[Polynomial, Monomial] = factor1
		self.factor2: Union[Polynomial, Monomial] = factor2

	def _multiply_monomials(self) -> Monomial:
		"""	Returns a product of two monomials."""
		const = self.factor1.const * self.factor2.const
		factors = {}
		variables = self.factor1.variables | self.factor2.variables
		for var_i in variables:
			deg1 = self.factor1.factors.get(var_i, 0)
			deg2 = self.factor2.factors.get(var_i, 0)
			factors[var_i] = deg1 + deg2
		return Monomial(factors, const)

	def _multiply_polynomials(self) -> Polynomial:
		""" Returns a product of two polinomials."""
		monomials = []
		for monomial_1, monomial_2 in product(self.factor1.monomials, self.factor2.monomials):
			monomials.append(Product(monomial_1, monomial_2)._multiply_monomials())
		return Polynomial(monomials)

	def multiply(self) -> Union[Polynomial, Monomial]:
		""" Returns a product of two Polynomials/Monomials."""
		if isinstance(self.factor1, Polynomial):
			return self._multiply_polynomials()
		else:
			return self._multiply_monomials()


class Derivative(FunctionExpression):
	"""
	Этот класс создан, чтобы находить производную для FunctionExpression
	Его основной метод - find - возвращает объект типа FunctionExpression, который
	и является производной входного FunctionExpression.
	"""
	def __init__(self, function: FunctionExpression, var: str):
		"""	
		:param function: a function that will be differentiated;
		:param var: a variable of differentiation.
		"""
		super().__init__(function.dividend, function.divisor)
		self.var: str = var

	def _differentiate_monomial(self, monomial: Monomial) -> Monomial:
		""" Returns a derivative of a monomial."""
		if self.var not in monomial.factors or monomial.factors[self.var] == 0:
			return Monomial.zero()
		else:
			const = monomial.const * monomial.factors[self.var]
			factors = deepcopy(monomial.factors)
			factors[self.var] -= 1
			return Monomial(factors, const)

	def _differentiate_polynomial(self, polynomial: Polynomial) -> Polynomial:
		""" Returns a derivative of a polynomial."""
		monomials = []
		for monomial in polynomial.monomials:
			monomials.append(self._differentiate_monomial(monomial))
		return Polynomial(monomials)

	def _find(self) -> FunctionExpression:
		""" Returns a derivative of a fraction(FunctionExpression)."""
		divisor = self.divisor
		if self.var in self.divisor.variables:
			monomials = []
			first_term = Product(self._differentiate_polynomial(self.dividend), self.divisor).multiply()
			second_term = Product(self.dividend, self._differentiate_polynomial(self.divisor)).multiply()
			second_term.minus()
			monomials += first_term.monomials + second_term.monomials
			dividend = Polynomial(monomials)
			divisor.square()
		else:
			dividend = self._differentiate_polynomial(self.dividend)
		return FunctionExpression(dividend, divisor)
