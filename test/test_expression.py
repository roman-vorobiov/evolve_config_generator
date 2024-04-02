from utils.expression import *
import pytest


class DummyNumeric(UnaryExpression, NumericExpression):
    pass


class DummyBoolean(UnaryExpression, BooleanExpression):
    pass


def compare(l, r):
    assert repr(l) == repr(r)


def test_stack():
    assert current_condition() is True

    with DummyNumeric('building1'):
        compare(current_condition(), DummyNumeric('building1'))

        with DummyNumeric('building2'):
            compare(current_condition(), all_of(DummyNumeric('building1'), DummyNumeric('building2')).reduce())

        compare(current_condition(), DummyNumeric('building1'))

    assert current_condition() is True


def test_eval_from_number():
    assert Number(123).to_eval_string() == '123'


def test_eval_from_string():
    assert String('asd').to_eval_string() == '"asd"'


def test_eval_from_boolean():
    assert Boolean(True).to_eval_string() == 'true'


def test_eval_from_eval():
    assert Eval('a + b').to_eval_string() == '(a + b)'


def test_eval_from_unary():
    assert DummyNumeric('asd').to_eval_string() == \
        'checkTypes.DummyNumeric.fn("asd")'


@pytest.mark.parametrize("op_in, op_out", [('==', '=='), ('<', '<'), ('AND', '&&'), ('OR', '||'), ('AND!', '&&!'), ('OR!', '||!')])
def test_eval_from_binary(op_in, op_out):
    assert BinaryExpression(DummyNumeric('asd'), op_in, DummyNumeric(123)).to_eval_string() == \
        f'checkTypes.DummyNumeric.fn("asd") {op_out} checkTypes.DummyNumeric.fn(123)'


def test_eval_from_reduce():
    assert all_of(DummyNumeric('asd') > DummyNumeric(123), DummyBoolean('fgh')).to_eval_string() == \
        '((checkTypes.DummyNumeric.fn("asd") > checkTypes.DummyNumeric.fn(123)) && checkTypes.DummyBoolean.fn("fgh"))'


def test_compose_unary_with_unary():
    compare(
        DummyBoolean(123) & DummyBoolean(456),
        BinaryExpression(DummyBoolean(123), 'AND', DummyBoolean(456))
    )


def test_compose_unary_with_binary():
    compare(
        DummyBoolean(123) & (DummyNumeric(456) > 0),
        BinaryExpression(DummyBoolean(123), 'AND', Eval('checkTypes.DummyNumeric.fn(456) > 0'))
    )


def test_compose_unary_with_negated():
    compare(
        DummyBoolean(123) & (DummyBoolean(456) == False),
        BinaryExpression(DummyBoolean(123), 'AND!', DummyBoolean(456))
    )


def test_compose_unary_with_reduce():
    compare(
        DummyNumeric(123) == any_of(456, 789),
        any_of(DummyNumeric(123) == Number(456), DummyNumeric(123) == Number(789))
    )


def test_compose_binary_with_unary():
    compare(
        (DummyNumeric(123) > 0) & DummyBoolean(456),
        BinaryExpression(Eval('checkTypes.DummyNumeric.fn(123) > 0'), 'AND', DummyBoolean(456))
    )


def test_compose_binary_with_binary():
    compare(
        (DummyNumeric(123) > 0) & (DummyNumeric(456) < 0),
        BinaryExpression(Eval('checkTypes.DummyNumeric.fn(123) > 0'), 'AND', Eval('checkTypes.DummyNumeric.fn(456) < 0'))
    )


def test_compose_binary_with_reduce():
    compare(
        (DummyNumeric(123) > 0) & any_of(DummyBoolean(456), DummyBoolean(789)),
        any_of((DummyNumeric(123) > 0) & DummyBoolean(456), (DummyNumeric(123) > 0) & DummyBoolean(789))
    )


def test_compose_negated_with_unary():
    compare(
        (DummyBoolean(123) == False) & DummyBoolean(456),
        BinaryExpression(DummyBoolean(456), 'AND!', DummyBoolean(123))
    )


def test_reverse_reduce():
    compare(
        DummyNumeric(all_of(123, 456)),
        all_of(DummyNumeric(123), DummyNumeric(456))
    )


def test_unary_expression_from_int():
    compare(unary_expression(123), Number(123))


def test_unary_expression_from_float():
    compare(unary_expression(1.23), Number(1.23))


def test_unary_expression_from_string():
    compare(unary_expression('asd'), String('asd'))


def test_unary_expression_from_boolean():
    compare(unary_expression(True), Boolean(True))


def test_unary_expression_from_unary():
    compare(unary_expression(DummyNumeric('asd')), DummyNumeric('asd'))


def test_unary_expression_from_binary():
    compare(
        unary_expression(DummyNumeric('asd') > 0),
        Eval('checkTypes.DummyNumeric.fn("asd") > 0')
    )


def test_unary_expression_from_reduce():
    compare(
        unary_expression(any_of(DummyNumeric('asd'), DummyNumeric('fgh') > 0)),
        Eval('checkTypes.DummyNumeric.fn("asd") || (checkTypes.DummyNumeric.fn("fgh") > 0)')
    )


def test_binary_expression_from_binary():
    compare(
        binary_expression(DummyBoolean(123) | DummyBoolean(456)),
        BinaryExpression(DummyBoolean(123), 'OR', DummyBoolean(456))
    )


def test_binary_expression_from_unary():
    with pytest.raises(Exception):
        binary_expression(DummyNumeric('asd'))


def test_binary_expression_from_unary_boolean():
    compare(
        binary_expression(DummyBoolean('asd')),
        BinaryExpression(DummyBoolean('asd'), '==', Boolean(True))
    )


def test_binary_expression_from_unary_negated():
    compare(
        binary_expression(~DummyBoolean('asd')),
        BinaryExpression(DummyBoolean('asd'), '==', Boolean(False))
    )


def test_binary_expression_from_reduce():
    compare(
        binary_expression(any_of(DummyNumeric('asd'), DummyNumeric('fgh') > 0)),
        BinaryExpression(DummyNumeric('asd'), 'OR', Eval('checkTypes.DummyNumeric.fn("fgh") > 0'))
    )
