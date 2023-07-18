#!/usr/bin/python3
import sys
import re

from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPlainTextEdit
from PyQt6.QtWidgets import QPushButton, QApplication
from PyQt6.QtGui import QGuiApplication
from PyQt6 import uic

from utils.translate import interpret, interpret_reverse


# noinspection PyUnresolvedReferences
class AppConverter(QMainWindow):

    def __init__(self):
        super().__init__()
        qr = self.frameGeometry()
        qr.moveCenter(QGuiApplication.primaryScreen().availableGeometry().center())
        self.move(qr.topLeft())

        uic.loadUi('./utils/main.ui', self)
        # **********************************************************************************
        # Работа с выражениями
        self.qline_expression: QLineEdit  # Строка для ввода выражения
        self.terminal: QPlainTextEdit  # Терминал введённых выражений
        self.qbtn_add_expression: QPushButton  # Кнопка для добавления выражения в терминал
        self.qbtn_add_expression.clicked.connect(self.add_expression)

        self.qbtn_zero_expressions: QPushButton  # Кнопка для сброса введённых выражений
        self.qbtn_zero_expressions.clicked.connect(self.zero_expressions)

        self.qline_diff_var: QLineEdit  # Принимаем нужную переменную
        # **********************************************************************************
        self.qbtn_start: QPushButton  # Найти производную
        self.qbtn_start.clicked.connect(self.start)
        self.result_display: QPlainTextEdit  # Отображение результата

        self.variables_display: QPlainTextEdit  # Ввод переменных
        self.qbtn_count: QPushButton
        self.qbtn_count.clicked.connect(self.count)

        self.math_expr = None

    def add_expression(self):
        expression = self.qline_expression.text()
        self.qline_expression.setText("")
        self.terminal.appendPlainText(expression+'\n')

    def zero_expressions(self):
        self.terminal.setPlainText("")

    def start(self):
        expressions = [expr for expr in self.terminal.toPlainText().split('\n') if expr]
        diff_var = self.qline_diff_var.text()
        if expressions and diff_var:
            math_expr = interpret(expressions)
            math_expr.differentiate(diff_var)
            self.result_display.setPlainText(f"Derivative is: {interpret_reverse(math_expr)}")
            self.math_expr = math_expr
            vars_text = f""
            for var in math_expr.variables:
                vars_text += f"{var} = \n"
            self.variables_display.setPlainText(vars_text)
            self.variables_display.setReadOnly(False)

    def count(self):
        text_vars = self.variables_display.toPlainText()
        args = {}
        for couple in text_vars.split('\n'):
            if couple:
                var, value = re.split(r'\s+=\s+', couple)
                args[var] = float(value)
        result = self.math_expr.value(args)
        self.result_display.appendPlainText(f"\nDerivative's value is: {result}")


if __name__ == '__main__':
    main_app = QApplication([])
    converter_app = AppConverter()
    converter_app.show()
    sys.exit(main_app.exec())
