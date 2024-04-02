# Generate the config for the Evolve script

```
usage: app.py [-h] [--base BASE] [--out OUT] [--print] [--pretty]

Generate the config for the Evolve script

optional arguments:
  -h, --help   show this help message and exit
  --base BASE  Path to the base (default) config.json. Any changes will be applied on top of the values that are in this config.
  --out OUT    Path to save the generated config.json to.
  --print      Print the result to the console.
  --pretty     Add indentation and newlines to the resulting json.
```


```bash
# load `default.json`, apply your changes on top of it and save the result as `config.json`
python app.py --base default.json --out config.json

# print to console just your changes
python app.py --print --pretty
```

## Writing your own config

Update the `generate_config` function in `generate.py`. The `config` parameter is pretty much a regular python `dict` with a little syntax sugar on top of the `__setitem__` for easier override generation.

To override a setting just set the corresponding field. The usual syntax for lists/objects apply:

```python
def generate_config(config):
    config['autoTax'] = True
    config['prestigeType'] = 'bioseed'
    config['foreignHireMercMoneyStoragePercent'] = 50
    config['researchIgnore'].append('tech-combat_droids')
```

If you don't know what the specific key is you can open the default config and try to guess :)
Or `Ctrl + click` on the UI and it will tell you in the modal's title.

Many entities such as buildings or resources have different keys for weights, priority, auto-build etc.
Check out `utils/strings.py` for the whole list. Feel free to add more.
There are lists of internal names for tech and buildings in `utils/names.py` for lookup.

```python
config[build_max('city-lumber_yard')] = 20
config[auto_build('city-hospital')] = False
config[foundry_weight('Plywood')] = 1
config[trade_priority('Helium_3')] = 100
```

To add an override simply set the corresponding fields within a `with` statement with the condition (see `utils/overrides.py`):

```python
with TraitLevel('terrifying') != 0:
    config['foreignUnification'] = False
    config['foreignPolicySuperior'] = 'Sabotage'
```

You can also nest them:

```python
with SettingCurrent('prestigeType') == 'bioseed':
    config[auto_build('city-hospital')] = False

    with BuildingUnlocked('space-star_dock') == False:
        config[auto_build('city-biolab')] = True

    with ResearchComplete('tech-quantum_manufacturing'):
        config[auto_build('city-biolab')] = False
```

which is equivalent to

```python
with SettingCurrent('prestigeType') == 'bioseed':
    config[auto_build('city-hospital')] = False

with (SettingCurrent('prestigeType') == 'bioseed') & ~BuildingUnlocked('space-star_dock'):
    config[auto_build('city-biolab')] = True

with (SettingCurrent('prestigeType') == 'bioseed') & ResearchComplete('tech-quantum_manufacturing'):
    config[auto_build('city-biolab')] = False
```

Since python does not allow to override logical `and`, `or` and `not`, the next best thing is arithmetic operators. Be careful, however, as they have different precedence than their logical counterparts - just use parentheses if unsure.


You can also assign these expressions directly, which is translated into an `A?B` override:

```python
config[trade_priority('Coal')] = ResourceRatio('Coal')

with SettingCurrent('prestigeType') == 'bioseed':
    config[trade_priority('Oil')] = ResourceRatio('Oil')

# same as

add_override(config, trade_priority('Coal'), None, BinaryExpression(Boolean(True), 'A?B', ResourceRatio('Coal')))
add_override(config, trade_priority('Coal'), None, BinaryExpression(SettingCurrent('prestigeType') == 'bioseed', 'A?B', ResourceRatio('Oil')))
```

Boolean expressions are optimized on the top level (outside of any `with` statements):

```python
config[auto_arpa('monument')] = ProjectCount(project('monument')) < 50

# same as

config[auto_arpa('monument')] = False

with ProjectCount(project('monument')) < 50:
    config[auto_arpa('monument')] = True
```

You can combine multiple overrides in the same statement (which can be nested too):

```python
config['govGovernor'] = {
    'entrepreneur': SettingCurrent('prestigeType') == 'mad',
    'spiritual': (SettingCurrent('prestigeType') == 'bioseed') | (SettingCurrent('prestigeType') == 'whitehole'),
    'sports': '*' # special value that means "otherwise"
}

# same as

config['govGovernor'] = 'sports'

with SettingCurrent('prestigeType') == 'mad':
    config['govGovernor'] = 'entrepreneur'

with (SettingCurrent('prestigeType') == 'bioseed') | (SettingCurrent('prestigeType') == 'whitehole'):
    config['govGovernor'] = 'spiritual'
```

Fold expressions such as `any_of` or `all_of` can be used to combine conditions, which allow more optimizations than the `|` or `&` operators:

```python
config[auto_arpa('monument')] = any_of(
    ResourceQuantity('Morale') >= ResourceStorage('Morale'),
    ProjectCount(project('monument')) < 2
)

# same as

config[auto_arpa('monument')] = False

with ResourceQuantity('Morale') >= ResourceStorage('Morale'):
    config[auto_arpa('monument')] = True

with ProjectCount(project('monument')) < 2:
    config[auto_arpa('monument')] = True
```

Binary expressions are automatically converted to the corresponding `Eval` allowing you to compose them without limitations:

```python
(SettingCurrent('prestigeType') == 'mad') | (SettingCurrent('prestigeType') == 'bioseed') | (SettingCurrent('prestigeType') == 'whitehole')

# same as

Eval('(checkTypes.SettingCurrent.fn("prestigeType") == "mad" || checkTypes.SettingCurrent.fn("prestigeType") == "bioseed") || checkTypes.SettingCurrent.fn("prestigeType") == "whitehole"')
```

As a shorthand you can use `any_of` and `all_of` inside the constructor of a unary expression or a composition operand:

```python
ResourceDemanded(any_of('Infernite', 'Graphene'))
SettingCurrent('prestigeType') == any_of('mad', 'bioseed', 'whitehole')

# same as

any_of(ResourceDemanded('Infernite'), ResourceDemanded(('Graphene'))
any_of(SettingCurrent('prestigeType') == 'mad', SettingCurrent('prestigeType') == 'bioseed', SettingCurrent('prestigeType') == 'whitehole')
```

To add a trigger use the `add_trigger` function (see `utils/trigger.py`):

```python
add_trigger(config, Unlocked('tech-electricity'), Research('tech-electricity'))
```

If the second argument is a list, the actions after the first one will be added with the `Chain` requirement:

```python
add_trigger(config, Unlocked('tech-industrialization'), [
    Research('tech-industrialization'),
    Research('tech-diplomacy'),
    Research('tech-republic'),
    Research('tech-technocracy')
])

# same as

add_trigger(config, Unlocked('tech-industrialization'), Research('tech-industrialization'))
add_trigger(config, Chain(), Research('tech-diplomacy'))
add_trigger(config, Chain(), Research('tech-republic'))
add_trigger(config, Chain(), Research('tech-technocracy'))
```

Check out the tests to see how the python code is translated into JSON.
