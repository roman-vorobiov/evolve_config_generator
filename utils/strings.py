def auto_arpa(project):
    return f'arpa_{project}'


def arpa_weight(project):
    return f'arpa_w_{project}'


def arpa_max(project):
    return f'arpa_m_{project}'


def auto_build(struct):
    return f'bat{struct}'


def project(name):
    return f'arpa{name}'


def build_max(struct):
    return f'bld_m_{struct}'


def build_weight(struct):
    return f'bld_w_{struct}'


def auto_support(struct):
    return f'bld_s_{struct}'


def foundry_weight(craftable):
    return f'foundry_w_{craftable}'


def auto_buy(resource):
    return f'buy{resource}'


def auto_sell(resource):
    return f'sell{resource}'


def trade_enabled(resource):
    return f'res_trade_sell_{resource}'


def trade_priority(resource):
    return f'res_trade_p_{resource}'
