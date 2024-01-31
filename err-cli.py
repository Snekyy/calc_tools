#!/usr/bin/python3
from libs.translate import *
from libs.functions import *


def main():
	math_expr = interpret([input("Enter your formula: ")])
	args = {}
	args_errs = {}
	for var in math_expr.variables:
		args[var] = float(input(f"Enter value of {var} variable: "))
		args_errs[var] = float(input(f"Enter value of {var}'s error: "))
	res = []
	print("Значение величины: ", math_expr.value(args))
	print("Ее погрешность", math_expr.value_err(args, args_errs))

main()
