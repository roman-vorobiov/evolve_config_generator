import functools
from collections.abc import Iterable


override_context = []


def constant_to_string(value):
    if type(value) in {int, float}:
        return f'{value}'
    elif type(value) == str:
        return f'"{value}"'
    elif type(value) == bool:
        return 'true' if value else 'false'
    else:
        raise Exception(f'Unknown value type: {value}')


class Expression:
    def compose_with(self, other, op, fold=False):
        def invert(op):
            if op in {'AND', 'OR'}:
                return f'{op}!'
            else:
                raise Exception(f'Operator not inversable: {op}')

        def is_negated(arg):
            return isinstance(arg, BinaryExpression) \
                and arg.op == '==' \
                and isinstance(arg.r, Boolean) \
                and arg.r.value is False

        if not fold and isinstance(other, ReduceExpression):
            assert not isinstance(self, ReduceExpression)
            return type(other)([self.compose_with(e, op) for e in other.expressions])
        elif is_negated(self):
            return BinaryExpression(other, invert(op), self.l)
        elif is_negated(other):
            return BinaryExpression(self, invert(op), other.l)
        else:
            return BinaryExpression(self, op, other)

    def __eq__(self, other):
        return self.compose_with(other, '==')

    def __ne__(self, other):
        return self.compose_with(other, '!=')

    def __enter__(self):
        global override_context
        override_context.append(self)

    def __exit__(self, *args):
        global override_context
        override_context.pop()


class BooleanExpression(Expression):
    def __and__(self, other):
        return self.compose_with(other, 'AND')

    def __or__(self, other):
        return self.compose_with(other, 'OR')

    def __invert__(self):
        return self == False


class NumericExpression(Expression):
    def __lt__(self, other):
        return self.compose_with(other, '<')

    def __le__(self, other):
        return self.compose_with(other, '<=')

    def __gt__(self, other):
        return self.compose_with(other, '>')

    def __ge__(self, other):
        return self.compose_with(other, '>=')


class AnyExpression(BooleanExpression, NumericExpression):
    pass


class UnaryExpression(Expression):
    def __new__(cls, value):
        """F(any_of(A, B, C)) -> any_of(F(A), F(B), F(C))"""
        if isinstance(value, ReduceExpression):
            return type(value)([cls(v) for v in value.expressions])
        else:
            return super().__new__(cls)

    def __init__(self, value):
        self.type = type(self).__name__
        self.value = value

    def __repr__(self):
        return f'{self.type}({constant_to_string(self.value)})'

    def to_eval_string(self):
        return f'checkTypes.{self.type}.fn({constant_to_string(self.value)})'


class BinaryExpression(BooleanExpression):
    def __init__(self, l, op, r):
        self.l = unary_expression(l)
        self.r = unary_expression(r)
        self.op = op

    def __repr__(self):
        return f'{self.l} {self.op} {self.r}'

    def to_eval_string(self):
        op = self.op.replace('AND', '&&')
        op = op.replace('OR', '||')

        return f'{self.l.to_eval_string()} {op} {self.r.to_eval_string()}'


class ReduceExpression(BooleanExpression):
    def __init__(self, expressions, op, init):
        self.expressions = list(expressions)
        self.op = op
        self.init = unary_expression(init)

    def __repr__(self):
        return f'{self.expressions}.reduce({self.op}, default={self.init})'

    def to_eval_string(self):
        return unary_expression(self.reduce()).to_eval_string()

    def reduce(self):
        if len(self.expressions) == 0:
            return self.init
        else:
            return functools.reduce(lambda l, r: l.compose_with(r, self.op, True), self.expressions[1:], self.expressions[0])


class ConstantExpression(UnaryExpression):
    def to_eval_string(self):
        return constant_to_string(self.value)


class Number(ConstantExpression, NumericExpression):
    pass

class String(ConstantExpression):
    pass

class Boolean(ConstantExpression, BooleanExpression):
    pass

class Eval(UnaryExpression, AnyExpression):
    def to_eval_string(self):
        return f'({self.value})'

class AnyOf(ReduceExpression):
    def __init__(self, expressions):
        super().__init__(expressions, 'OR', False)

class AllOf(ReduceExpression):
    def __init__(self, expressions):
        super().__init__(expressions, 'AND', True)


def unary_expression(value):
    if isinstance(value, UnaryExpression):
        return value
    elif isinstance(value, BinaryExpression):
        return Eval(value.to_eval_string())
    elif isinstance(value, ReduceExpression):
        return unary_expression(value.reduce())
    elif type(value) in {int, float}:
        return Number(value)
    elif type(value) == str:
        return String(value)
    elif type(value) == bool:
        return Boolean(value)
    else:
        raise Exception(f'Unknown value type: {value}')


def binary_expression(value):
    if isinstance(value, BinaryExpression):
        return value
    elif isinstance(value, UnaryExpression) and isinstance(value, BooleanExpression):
        return value == True
    elif isinstance(value, ReduceExpression):
        return binary_expression(value.reduce())
    else:
        raise Exception(f'Unknown value type: {value}')


def any_of(*conditions):
    if len(conditions) == 1 and isinstance(conditions[0], Iterable):
        return AnyOf(conditions[0])
    else:
        return AnyOf(conditions)


def all_of(*conditions):
    if len(conditions) == 1 and isinstance(conditions[0], Iterable):
        return AllOf(conditions[0])
    else:
        return AllOf(conditions)


def current_condition():
    global override_context

    if len(override_context) == 0:
        return True
    else:
        return all_of(*override_context).reduce()
