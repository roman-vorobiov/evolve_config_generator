from .expression import (
    UnaryExpression,
    BooleanExpression,
    NumericExpression,
    AnyExpression,
    binary_expression
)


class BuildingAffordable(UnaryExpression, BooleanExpression): pass

class BuildingUnlocked(UnaryExpression, BooleanExpression): pass

class BuildingCount(UnaryExpression, NumericExpression): pass

class ProjectCount(UnaryExpression, NumericExpression): pass

class RaceId(UnaryExpression): pass

class ResearchComplete(UnaryExpression, BooleanExpression): pass

class ResourceDemanded(UnaryExpression, BooleanExpression): pass

class ResourceIncome(UnaryExpression, NumericExpression): pass

class ResourceQuantity(UnaryExpression, NumericExpression): pass

class ResourceRatio(UnaryExpression, NumericExpression): pass

class ResourceSatisfied(UnaryExpression, BooleanExpression): pass

class ResourceStorage(UnaryExpression, NumericExpression): pass

class ResourceUnlocked(UnaryExpression, BooleanExpression): pass

class SettingCurrent(UnaryExpression, AnyExpression): pass

class TraitLevel(UnaryExpression, NumericExpression): pass

class Challenge(UnaryExpression, BooleanExpression): pass

class ResetType(UnaryExpression, BooleanExpression): pass


def add_override(config, target, value, condition):
    condition = binary_expression(condition)

    config['overrides'].setdefault(target, []).append({
        'type1': condition.l.type,
        'arg1': condition.l.value,
        'cmp': condition.op,
        'type2': condition.r.type,
        'arg2': condition.r.value,
        'ret': value
    })
