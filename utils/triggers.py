class Requirement:
    def __init__(self, value='', count=1):
        self.value = value
        self.count = count

    def to_json(self):
        return {
            'requirementType': type(self).__name__.lower(),
            'requirementId': self.value,
            'requirementCount': self.count
        }


class Action:
    def __init__(self, value, count=1):
        self.value = value
        self.count = count

    def to_json(self):
        return {
            'actionType': type(self).__name__.lower(),
            'actionId': self.value,
            'actionCount': self.count
        }


class Built(Requirement): pass
class Researched(Requirement): pass
class Unlocked(Requirement): pass
class Chain(Requirement): pass

class Build(Action): pass
class Research(Action): pass


def add_trigger_single(config, requirement, action):
    idx = len(config['triggers'])
    config['triggers'].append({
        'seq': idx,
        'priority': idx,
        **requirement.to_json(),
        **action.to_json(),
        'complete': False
    })


def add_trigger(config, requirement, actions):
    if isinstance(actions, list):
        add_trigger_single(config, requirement, actions[0])
        for action in actions[1:]:
            add_trigger_single(config, Chain(), action)
    else:
        add_trigger_single(config, requirement, actions)
