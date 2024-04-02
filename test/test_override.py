from utils import *
import pytest


@pytest.fixture
def config():
    yield Config({ 'overrides': {} })


def test_assign_constant(config):
    config['key'] = 123

    assert config['key'] == 123
    assert 'key' not in config['overrides']


def test_assign_constant_with_context(config):
    with BuildingAffordable('building'):
        config['key'] = 123

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': 123
        }
    ]


def test_assign_unary_numeric_expression(config):
    config['key'] = ProjectCount('project')

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'Boolean',
            'arg1': True,
            'cmp': 'A?B',
            'type2': 'ProjectCount',
            'arg2': 'project',
            'ret': None
        }
    ]


def test_assign_unary_numeric_expression_with_context(config):
    with BuildingAffordable('building'):
        config['key'] = ProjectCount('project')

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': 'A?B',
            'type2': 'ProjectCount',
            'arg2': 'project',
            'ret': None
        }
    ]


def test_assign_unary_boolean_expression(config):
    config['key'] = BuildingAffordable('building')

    assert config['key'] == False
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': True
        }
    ]


def test_assign_unary_boolean_expression_with_context(config):
    with BuildingAffordable('building1'):
        config['key'] = BuildingUnlocked('building2')

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'A?B',
            'type2': 'BuildingUnlocked',
            'arg2': 'building2',
            'ret': None
        }
    ]


def test_assign_binary_expression(config):
    config['key'] = ProjectCount('project') > 0

    assert config['key'] == False
    assert config['overrides']['key'] == [
        {
            'type1': 'ProjectCount',
            'arg1': 'project',
            'cmp': '>',
            'type2': 'Number',
            'arg2': 0,
            'ret': True
        }
    ]


def test_assign_binary_expression_with_context(config):
    with BuildingAffordable('building'):
        config['key'] = ProjectCount('project') > 0

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': 'A?B',
            'type2': 'Eval',
            'arg2': 'checkTypes.ProjectCount.fn("project") > 0',
            'ret': None
        }
    ]


def test_assign_any_of(config):
    config['key'] = any_of(BuildingAffordable('building'), ProjectCount('project') > 0)

    assert config['key'] == False
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': True
        },
        {
            'type1': 'ProjectCount',
            'arg1': 'project',
            'cmp': '>',
            'type2': 'Number',
            'arg2': 0,
            'ret': True
        }
    ]


def test_assign_any_of_with_context(config):
    with BuildingAffordable('building1'):
        config['key'] = any_of(BuildingUnlocked('building2'), ProjectCount('project') > 0)

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'A?B',
            'type2': 'Eval',
            'arg2': 'checkTypes.BuildingUnlocked.fn("building2") || (checkTypes.ProjectCount.fn("project") > 0)',
            'ret': None
        }
    ]


def test_assign_all_of(config):
    config['key'] = all_of(BuildingUnlocked('building1'), BuildingAffordable('building2'))

    assert config['key'] == False
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingUnlocked',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'BuildingAffordable',
            'arg2': 'building2',
            'ret': True
        }
    ]


def test_assign_all_of_with_context(config):
    with BuildingUnlocked('building1'):
        config['key'] = all_of(BuildingAffordable('building2'), BuildingAffordable('building3'))

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingUnlocked',
            'arg1': 'building1',
            'cmp': 'A?B',
            'type2': 'Eval',
            'arg2': 'checkTypes.BuildingAffordable.fn("building2") && checkTypes.BuildingAffordable.fn("building3")',
            'ret': None
        }
    ]


def test_assign_pattern_matching_no_default(config):
    config['key'] = {
        123: BuildingAffordable('building'),
        456: ProjectCount('project') > 0
    }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': 123
        },
        {
            'type1': 'ProjectCount',
            'arg1': 'project',
            'cmp': '>',
            'type2': 'Number',
            'arg2': 0,
            'ret': 456
        }
    ]


def test_assign_pattern_matching_no_default_with_context(config):
    with BuildingAffordable('building1'):
        config['key'] = {
            123: BuildingUnlocked('building2'),
            456: ProjectCount('project') > 0
        }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'BuildingUnlocked',
            'arg2': 'building2',
            'ret': 123
        },
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'Eval',
            'arg2': 'checkTypes.ProjectCount.fn("project") > 0',
            'ret': 456
        }
    ]


def test_assign_pattern_matching_with_default(config):
    config['key'] = {
        123: BuildingAffordable('building'),
        456: ProjectCount('project') > 0,
        789: '*'
    }

    assert config['key'] == 789
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': 123
        },
        {
            'type1': 'ProjectCount',
            'arg1': 'project',
            'cmp': '>',
            'type2': 'Number',
            'arg2': 0,
            'ret': 456
        }
    ]


def test_assign_pattern_matching_with_default_with_context(config):
    with BuildingAffordable('building1'):
        config['key'] = {
            123: BuildingUnlocked('building2'),
            456: ProjectCount('project') > 0,
            789: '*'
        }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'BuildingUnlocked',
            'arg2': 'building2',
            'ret': 123
        },
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'Eval',
            'arg2': 'checkTypes.ProjectCount.fn("project") > 0',
            'ret': 456
        },
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': 789
        }
    ]


def test_assign_pattern_matching_nested_any_of(config):
    config['key'] = {
        123: any_of(BuildingAffordable('building'), ProjectCount('project') > 0)
    }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building',
            'cmp': '==',
            'type2': 'Boolean',
            'arg2': True,
            'ret': 123
        },
        {
            'type1': 'ProjectCount',
            'arg1': 'project',
            'cmp': '>',
            'type2': 'Number',
            'arg2': 0,
            'ret': 123
        }
    ]


def test_assign_pattern_matching_nested_any_of_with_context(config):
    with BuildingAffordable('building1'):
        config['key'] = {
            123: any_of(BuildingUnlocked('building2'), ProjectCount('project') > 0)
        }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'BuildingUnlocked',
            'arg2': 'building2',
            'ret': 123
        },
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'Eval',
            'arg2': 'checkTypes.ProjectCount.fn("project") > 0',
            'ret': 123
        }
    ]


def test_assign_pattern_matching_nested_all_of(config):
    config['key'] = {
        123: all_of(BuildingAffordable('building1'), BuildingAffordable('building2'))
    }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingAffordable',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'BuildingAffordable',
            'arg2': 'building2',
            'ret': 123
        }
    ]


def test_assign_pattern_matching_nested_all_of_with_context(config):
    with BuildingUnlocked('building1'):
        config['key'] = {
            123: all_of(BuildingAffordable('building2'), BuildingAffordable('building3'))
        }

    assert 'key' not in config
    assert config['overrides']['key'] == [
        {
            'type1': 'BuildingUnlocked',
            'arg1': 'building1',
            'cmp': 'AND',
            'type2': 'Eval',
            'arg2': 'checkTypes.BuildingAffordable.fn("building2") && checkTypes.BuildingAffordable.fn("building3")',
            'ret': 123
        }
    ]
