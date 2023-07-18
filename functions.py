from copy import deepcopy
from typing import Union
from itertools import product


class Monomial:
	""" A model of a monomial (product of many variables)

		Attributes:
			const: a integer, coefficient k in k*x^2*y^8*z^3, is a 1 by default.
			factors: a dict of strings-integers, factors names(i.e. variables letters in monomial)
				and their degrees in monomial.
				E.g.: {"x": degree_x, "y": degree_y, ...}.
				Factors may be an empty dict, if the monomial is just a constant.
			variables: a set of strings, contains variables letter used in monomial product.
				E.g. {"x", "y", ...}.
	"""

	def __hash__(self):
		""" Is needed for Polynomial.__eq__"""
		return hash((self.const, tuple(self.factors.items())))

	def __eq__(self, another: 'Monomial'):
		""" Two monomials equal, when all their factors are equal,
			i.e. the constant and factors.

			:param another: second argument in the equality, a Monomial object.
		"""
		if self.factors == another.factors and self.const == another.const:
			return True
		return False
	
	def __init__(self, factors: dict[str, int], const: float = 1.0):
		"""	Initialize self, creates variables attr using Monomial._count_variables"""
		self.factors = factors
		self.const = const
		self.variables: set = self._count_variables()

	@staticmethod
	def zero():
		""" Creates and returns monomial identity to zero"""
		zero = Monomial({}, 0)
		zero.variables = set()
		return zero

	@staticmethod
	def one():
		""" Creates and returns monomial identity to one"""
		one = Monomial({}, 1)
		one.variables = set()
		return one

	def _count_variables(self) -> set:
		""" Returns a set of variables(variables letter, i.e. strings), used in monomial"""
		return set(self.factors.keys())

	def _cleanup(self) -> None:
		""" Makes monomial's expression(self) more simple:
			if the monomial's const is a zero, changes the Monomials's 
			factors to a Monomial.zero().factors, i. e an empty dict;
			if the monomial has zeros in factors.values(), i. e.
			variables in a monomials's product at a zero degrees,
			deletes those useless factors. Updates the variables at the end.
		"""
		old_factors: dict = self.factors
		if self.const == 0:
			self.factors = Monomial.zero().factors
		else:
			new_factors = {}
			for var, degree in old_factors.items():
				if degree != 0:
					new_factors[var] = degree
			self.factors = new_factors
		self.variables = self._count_variables()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a monomial

			:param args: dict of str-float, i.e. values of variables in monomial.
		"""
		value = self.const
		for key in args:
			if key in self.variables:
				value *= (args[key] ** self.factors[key])
		return value 


class Polynomial:
	""" A model of a polynomial (sum of monomials)

		Attributes:
			monomials: a list of monomials, i.e. terms(monomials) in the sum.
			variables: a set of strings, which contains variables letter
				used in monomial product, e.g. {"x", "y", ...}.
	"""

	def __eq__(self, another: 'Polynomial'):
		""" Two polynomials equal, when they have the same monomials,
			i.e. one set of monomials is equal to another set of monomials.

			:param another: second argument in the equality, i.e. a Polynomial.
		"""
		if set(self.monomials) == set(another.monomials):
			return True
		else:
			return False

	def __init__(self, monomials: list[Monomial]):
		""" Initialize self, creates variables attr using Polynomial._count_variables"""
		self.monomials = monomials
		self.variables: set = self._count_variables()

	@staticmethod
	def zero():
		""" Creates and returns polynomial identity to zero"""
		zero = Polynomial([Monomial.zero()])
		zero.variables = set()
		return zero

	@staticmethod
	def one():
		""" Creates and returns polynomial identity to one"""
		one = Polynomial([Monomial.one()])
		one.variables = set()
		return one

	def _count_variables(self) -> set:
		""" Returns a set of variables(variables letter, i.e. strings)
			used in polynomial, i.e. union of sets of variables of all monomials
		"""
		variables = set()
		for monomial in self.monomials:
			variables |= monomial.variables
		return variables

	def _cleanup(self) -> None:
		""" Makes polynomial's expression(self) more simple:
			apply Monomial._cleanup to every monomial in polinomial,
			combines like terms using Polynomial._combine_like_terms, which
			removes zero-monomials and updates variables.
		"""
		for monomial in self.monomials:
			monomial._cleanup()
		self._combine_like_terms()

	def _combine_like_terms(self) -> None:
		""" Combines like terms in the polynomial and removes zero-monomials"""
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
			if const != 0:
				new_monomials.append(Monomial(factors, const))
		# if monomials is empty, i.e. sum of monomials is equal to zero
		# so even a zero-monomial wasn't included, 
		# fixing that adding zero-monomial to monomials
		if len(new_monomials) == 0:
			self.monomials = Polynomial.zero().monomials
		else:
			self.monomials = new_monomials
		self.variables = self._count_variables()

	def square(self) -> None:
		""" Squares the polynomial"""
		self.monomials = Product(self, self).multiply().monomials

	def minus(self) -> None:
		""" Returns the polynomial mulitplied on a -1, i. e.
			changes a sign of the polynomial
		""" 
		minus_one_monomial = Monomial({}, -1)
		minus_one_polynomial = Polynomial([minus_one_monomial])
		self.monomials = Product(self, minus_one_polynomial).multiply().monomials

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a polynomial

			param args: dict of str-float; values of variables in polynomial.
		"""
		return sum([monomial.value(args) for monomial in self.monomials])


class RationalFunction:
	""" A model of a rational function (fraction of polynomials)

		Attributes:
			dividend: a polynomial in numerator;
			divisor: a polynomial in denumerator;
			variables: a set of strings, which contains variables letter
				used in rational function, e.g. {"x", "y", ...}.
	"""

	def __eq__(self, another: 'RationalFunction'):
		""" Two rational functions equal when: 1) dividend are zeros;
			2) dividend of one equals to dividend of another one and 
			divisor of one equals to dividinnd of another one.
			
			:param another: second argument in equality, a RationalFunction object
		"""
		if self.dividend == another.dividend and self.divisor == another.divisor:
			return True
		elif self.dividend == Polynomial.zero() and another.dividend == Polynomial.zero():
			return True
		else:
			return False

	def __init__(self, dividend: Polynomial, divisor: Polynomial):
		""" Initialize self and create variables attr using RationalFunction._count_variables

			:param dividend: polynomial in numerator (i.e. dividend);
			:param divisor: polynomial in denumerator (i.e. divisor).
		"""
		self.dividend: Polynomial = dividend
		self.divisor: Polynomial = divisor
		self.variables: set = self._count_variables()

	@staticmethod
	def zero():
		""" Creates and returns rational function identity to zero"""
		zero = RationalFunction(Polynomial.zero(), Polynomial.one())
		zero.variables = set()
		return zero

	@staticmethod
	def one():
		""" Creates and returns rational function identity to one"""
		one = RationalFunction(Polynomial.one(), Polynomial.one())
		one.variables = set()
		return one

	def _count_variables(self) -> set:
		""" Returns set of variables in MathExpression,
			i.e. in union of polynom-dividend variables and 
			polynom-divisor variables
		"""
		return self.dividend.variables | self.divisor.variables

	def _cleanup(self) -> None:
		""" Applies RationalFunction.__cleaup to poly_dividend, poly_divisor
			and updates the variables
		"""
		self.dividend._cleanup()
		self.divisor._cleanup()
		if self.dividend == Polynomial.zero():
			self.divisor = Polynomial.one()
		self.variables = self._count_variables()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a value of a rational function

			param args: dict of str-float; values of variables in polynomial.
		"""
		return self.dividend.value(args)/self.divisor.value(args)


class MathExpression:
	""" A model of a sum of a rational functions.

		Attributes:
			expression: a list of rational functions, i.e. terms in the sum;
			variables: a set of strings, which contains variables letter
				used in math expresstion, e.g. {"x", "y", ...}.
	"""

	def __init__(self, expression: list[RationalFunction]):
		""" Initialize self, creates variables attr using MathExpression._count_variables
			and apply MathExpression.__cleanup to self.
		
			:param expression: a list of a RationalFunction objects.
		"""
		self.expression: list[RationalFunction] = expression
		# Variables used in a sum of rational functions (i.e MathExpression)
		self.variables: set = self._count_variables()
		# Simplifing the expression after user entering it
		self.__cleanup()

	def _count_variables(self) -> set:
		""" Returns set of variables in union of all
			RationalFunctions in self.expression, i.e. returns
			variables, which are used in the sum of rational functions.
		"""
		variables = set()
		for func_expr in self.expression:
			variables = variables | func_expr.variables
		return variables

	def __cleanup(self) -> None:
		""" Applies RationalFunction._cleanup to every RationalFunction in the MathExpression,
			removes zero-RationalFunctions and updates variables
		"""
		for func_expr in self.expression:
			func_expr._cleanup()
			if func_expr == RationalFunction.zero():
				self.expression.remove(func_expr)
		if len(self.expression) == 0:
			self.expression.append(RationalFunction.zero())
		self.variables = self._count_variables()
		
	def differentiate(self, var: str) -> None:
		""" Differentiates itself (MathExpression), i.e. finds
			derivatives of every RationalFunction(rational function) in 
			that MathExpression(sum) and changes expression atr
			in that MathExpression

			:param var: A variable of a differentiation. E.g. var="x".
		"""
		self.expression = Derivative(var)._diff(self).expression
		self.__cleanup()

	def value(self, args: dict[str, float]) -> float:
		""" Returns a sum of FunctionExprestion's values in self.expression.

			:param args: len(self.variables) should be equal to len(args);
			:return: sum of RationalFunctions' values.
		"""
		# validation of entered agrs
		assert set(args.keys()) == self.variables
		return sum([func_expr.value(args) for func_expr in self.expression])


class Product:
	"""	A model of a product of Polynomials/Monomials
	
		Attributes:
			factor1: a polynomial or a monomial which is a factor in the product;
			factor2: the same.
	"""

	def __init__(self, factor1: Union[Polynomial, Monomial], factor2: Union[Polynomial, Monomial]):
		""" :param factor1: a polynomial or a monomial which is a factor in the product;
			:param factor2: the same
		"""
		assert type(factor1) == type(factor2)
		self.factor1: Union[Polynomial, Monomial] = factor1
		self.factor2: Union[Polynomial, Monomial] = factor2

	def __multiply_monomials(self) -> Monomial:
		"""	Returns a product of two monomials"""
		const = self.factor1.const * self.factor2.const
		factors = {}
		variables = self.factor1.variables | self.factor2.variables
		for var_i in variables:
			deg1 = self.factor1.factors.get(var_i, 0)
			deg2 = self.factor2.factors.get(var_i, 0)
			factors[var_i] = deg1 + deg2
		return Monomial(factors, const)

	def __multiply_polynomials(self) -> Polynomial:
		""" Returns a product of two polinomials"""
		monomials = []
		for monomial_1, monomial_2 in product(self.factor1.monomials, self.factor2.monomials):
			monomials.append(Product(monomial_1, monomial_2).__multiply_monomials())
		poly_product = Polynomial(monomials)
		poly_product._combine_like_terms()
		poly_product.variables = poly_product._count_variables()
		return poly_product

	def multiply(self) -> Union[Polynomial, Monomial]:
		""" Returns a product of two Polynomials/Monomials"""
		if isinstance(self.factor1, Polynomial):
			return self.__multiply_polynomials()
		else:
			return self.__multiply_monomials()


class Derivative:
	""" Derivative class is used for creating a MathExpression object,
		which is a derivative of a Derivative._diff parameter

		Attributes:
			var: a strings, letter; a variable of differentiation.
	"""
	def __init__(self, var: str):
		"""	:param var: a variable of differentiation"""
		self.var: str = var

	def __differentiate_monomial(self, monomial: Monomial) -> Monomial:
		""" Returns a Monomial object - derivative of a monomial"""
		if self.var not in monomial.factors:
			return Monomial.zero()
		else:
			const = monomial.const * monomial.factors[self.var]
			factors = deepcopy(monomial.factors)
			factors[self.var] -= 1
			deriv_monomial = Monomial(factors, const)
			return deriv_monomial

	def __differentiate_polynomial(self, polynomial: Polynomial) -> Polynomial:
		""" Returns a Polynomial - derivative of a polynomial"""
		monomials = []
		for monomial in polynomial.monomials:
			monomials.append(self.__differentiate_monomial(monomial))
		poly_deriv = Polynomial(monomials)
		poly_deriv._cleanup()
		poly_deriv.variables = poly_deriv._count_variables()
		return poly_deriv

	def _diff(self, function: MathExpression) -> MathExpression:
		""" Returns a MathExpression - derivative of a MathExpression"""
		deriv_expr = []
		for func_expr in function.expression:
			divisor = deepcopy(func_expr.divisor)
			dividend = deepcopy(func_expr.dividend)
			if self.var in divisor.variables:
				first_term = Product(self.__differentiate_polynomial(dividend), divisor).multiply()
				second_term = Product(dividend, self.__differentiate_polynomial(divisor)).multiply()
				second_term.minus()
				monomials = first_term.monomials + second_term.monomials
				dividend = Polynomial(monomials)
				divisor.square()
			else:
				dividend = self.__differentiate_polynomial(dividend)
			deriv_expr.append(RationalFunction(dividend, divisor))
		return MathExpression(deriv_expr)
