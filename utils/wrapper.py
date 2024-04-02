from .expression import Expression, BooleanExpression, BinaryExpression, AnyOf, current_condition
from .overrides import add_override
from .triggers import add_trigger


def unroll(condition):
    if isinstance(condition, AnyOf):
        # not necessary but multiple smaller overrides is better than 1 reduce
        assert len(condition.expressions) != 0
        for c in condition.expressions:
            with c:
                yield
    elif isinstance(condition, BooleanExpression):
        with condition:
            yield
    elif condition == True or condition == '*':
        yield
    else:
        raise Exception(f'Unknown condition: {condition}')


class Config(dict):
    def __setitem__(self, key, value):
        condition = current_condition()

        # config[key] = { value: condition, ... }
        if isinstance(value, dict):
            for v, condition in value.items():
                for _ in unroll(condition):
                    self[key] = v
        # config[key] = condition
        elif condition is True and isinstance(value, BooleanExpression):
            # not necessary but "True if condition else False" is better than "condition if True"
            for _ in unroll(value):
                self[key] = True
            self[key] = False
        # config[key] = value
        else:
            if isinstance(value, Expression):
                condition = BinaryExpression(condition, 'A?B', value)
                value = None

            if condition is True:
                super().__setitem__(key, value)
            else:
                add_override(self, key, value, condition)
