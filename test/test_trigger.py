from utils import *
import pytest


@pytest.fixture
def config():
    yield Config({ 'triggers': [] })


def test_single(config):
    add_trigger(config, Unlocked('building1', 2), Build('building2', 3))

    assert config['triggers'] == [
        {
            'seq': 0,
            'priority': 0,
            'requirementType': 'unlocked',
            'requirementId': 'building1',
            'requirementCount': 2,
            'actionType': 'build',
            'actionId': 'building2',
            'actionCount': 3,
            'complete': False
        }
    ]


def test_default_count(config):
    add_trigger(config, Unlocked('building1'), Build('building2'))

    assert config['triggers'] == [
        {
            'seq': 0,
            'priority': 0,
            'requirementType': 'unlocked',
            'requirementId': 'building1',
            'requirementCount': 1,
            'actionType': 'build',
            'actionId': 'building2',
            'actionCount': 1,
            'complete': False
        }
    ]


def test_multiple(config):
    add_trigger(config, Researched('tech1'), [Research('tech2'), Build('building2')])

    assert config['triggers'] == [
        {
            'seq': 0,
            'priority': 0,
            'requirementType': 'researched',
            'requirementId': 'tech1',
            'requirementCount': 1,
            'actionType': 'research',
            'actionId': 'tech2',
            'actionCount': 1,
            'complete': False
        },
        {
            'seq': 1,
            'priority': 1,
            'requirementType': 'chain',
            'requirementId': '',
            'requirementCount': 1,
            'actionType': 'build',
            'actionId': 'building2',
            'actionCount': 1,
            'complete': False
        }
    ]
