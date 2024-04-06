from utils import *


# We're redefining it below, so keep the reference to the original
add_trigger_impl = add_trigger


def generate_config(config):
    # utils

    def add_trigger(requirement, actions):
        add_trigger_impl(config, requirement, actions)

    def prioritize_research(tech):
        add_trigger(Unlocked(tech), Research(tech))

    # Generate triggers and overrides from scratch

    config['triggers'] = []
    config['overrides'] = {}

    # UI

    config['activeTargetsUI'] = True
    config['displayTotalDaysTypeInTopBar'] = True
    config['log_arpa'] = False
    config['log_attack'] = False
    config['log_prestige'] = True
    config['log_spying'] = False

    # Capabilities

    config['autoFight'] = True
    config['autoTax'] = True
    config['autoGovernment'] = True
    config['autoCraft'] = True
    config['autoTrigger'] = True
    config['autoBuild'] = True
    config['autoARPA'] = True
    config['autoPower'] = True
    config['autoStorage'] = True
    config['autoMarket'] = True
    config['autoResearch'] = True
    config['autoJobs'] = True
    config['autoCraftsmen'] = True
    config['autoQuarry'] = True
    config['autoSmelter'] = True
    config['autoFactory'] = True
    config['autoMiningDroid'] = True
    config['autoGraphenePlant'] = True
    config['autoGenetics'] = True
    config['autoEject'] = True

    # Prestige

    config['prestigeType'] = 'bioseed'
    config['prestigeMADWait'] = False
    config['prestigeBioseedProbes'] = 0

    # Challenges

    config['challenge_plasmid'] = True
    config['challenge_crispr'] = True
    config['challenge_trade'] = True
    config['challenge_craft'] = True

    # Don't craft from demanded resources

    config[foundry_weight('Plywood')] = { 0: ResourceDemanded('Lumber') }
    config[foundry_weight('Brick')] = { 0: ResourceDemanded('Cement') }
    config[foundry_weight('Wrought_Iron')] = { 0: ResourceDemanded('Iron') }
    config[foundry_weight('Sheet_Metal')] = { 0: ResourceDemanded('Aluminium') }
    config[foundry_weight('Mythril')] = { 0: ResourceDemanded(any_of('Iridium', 'Alloy')) }
    config[foundry_weight('Aerogel')] = { 0: ResourceDemanded(any_of('Infernite', 'Graphene')) }

    # Market

    # Ensure there is enough fuel
    config[trade_priority('Coal')] = { 100: ResourceRatio('Coal') < 0.02 }
    config[trade_priority('Oil')] = { 100: ResourceRatio('Oil') < 0.02 }
    config[trade_priority('Helium_3')] = { 100: ResourceRatio('Helium_3') < 0.02 }

    # Sometimes the script thinks a resource is in excess even though it's being used as a fuel
    # Make sure the fuel is still being imported even in these cases
    config['tradeRouteSellExcess'] = False

    for resource in RESOURCES:
        config[auto_buy(resource)] = True
        # Don't sell resources that can be used for crafting
        config[auto_sell(resource)] = resource not in {'Lumber', 'Cement', 'Iron', 'Aluminium'}
        # Only trade most profitable resources
        config[trade_enabled(resource)] = resource in {'Steel', 'Aluminium'}

    # Rush unification

    config['foreignUnification'] = True
    config['foreignPolicyInferior'] = 'Purchase'
    config['foreignPolicySuperior'] = 'Purchase'

    # unless playing balorg
    with TraitLevel('terrifying') != 0:
        config['foreignUnification'] = False
        config['foreignPolicySuperior'] = 'Sabotage'

    # Civics

    # Government
    config['govInterim'] = 'democracy'
    config['govFinal'] = 'technocracy'
    config['govSpace'] = 'federation'

    # Governor
    config['govGovernor'] = {
        'entrepreneur': ResetType('mad'),
        'spiritual': '*'
    }

    # Morale/Tax
    config['generalMinimumTaxRate'] = 0

    # Combat

    # Optimize advantage estimation
    config['foreignMinAdvantage'] = 48
    config['foreignMaxAdvantage'] = 52
    config['foreignProtect'] = 'never'
    config['foreignPowerRequired'] = 80

    # Mercs
    config['foreignHireMercMoneyStoragePercent'] = 50
    config['foreignHireMercCostLowerThanIncome'] = 5
    config['foreignHireMercDeadSoldiers'] = 4

    # Building progression

    add_trigger(Researched('tech-oil_well'), Build('city-oil_well'))
    add_trigger(Built('space-moon_mission'), Build('space-moon_base'))
    add_trigger(Built('space-moon_base'), Build('space-iridium_mine'))
    add_trigger(Built('space-moon_base'), Build('space-helium_mine'))
    add_trigger(Built('space-red_mission'), Build('space-spaceport'))
    add_trigger(Built('space-gas_moon_mission'), Build('space-outpost'))
    add_trigger(Built('space-belt_mission'), [
        Build('space-space_station'),
        Build('space-iridium_ship')
    ])
    add_trigger(Researched('tech-elerium_mining'), Build('space-elerium_ship'))
    add_trigger(Researched('tech-elerium_tech'), Build('space-elerium_contain'))

    # Force on Iridium Mining Ship until Elerium is discovered
    # config[auto_support('space-iridium_ship')] = { False: ResourceUnlocked('Elerium') == False }

    # Research progression

    prioritize_research('tech-rover')
    prioritize_research('tech-probes')
    prioritize_research('tech-starcharts')

    # Rush technocracy
    add_trigger(Unlocked('tech-industrialization'), [
        Research('tech-industrialization'),
        Research('tech-diplomacy'),
        Research('tech-republic'),
        Research('tech-technocracy')
    ])

    # Production research
    prioritize_research('tech-smelting')
    prioritize_research('tech-steel')
    prioritize_research('tech-bayer_process')
    prioritize_research('tech-oil_well')
    prioritize_research('tech-hunter_process')
    prioritize_research('tech-cambridge_process')
    prioritize_research('tech-graphene')
    prioritize_research('tech-stanene')

    # Power research
    prioritize_research('tech-electricity')
    prioritize_research('tech-oil_power')
    prioritize_research('tech-fission')

    # Other useful research
    prioritize_research('tech-tax_rates')
    prioritize_research('tech-trade')
    prioritize_research('tech-apartment')

    # Don't waste gems
    config['researchIgnore'].append('tech-combat_droids')
    config['researchIgnore'].append('tech-hellfire_furnace')

    # ARPA limits

    config[arpa_max('railway')] = 10

    config[auto_arpa('monument')] = any_of(
        # need for more max morale
        ResourceQuantity('Morale') >= ResourceStorage('Morale'),
        # unlock tourism
        ProjectCount(project('monument')) < 2
    )

    # 50 are needed for a banana task
    with Challenge('banana'):
        config[auto_arpa('monument')] = ProjectCount(project('monument')) < 50

    with ResetType('bioseed'):
        config[arpa_max('stock_exchange')] = 10
        config[arpa_max('railway')] = 1

    # Building priority

    # Prioritize production of demanded resources
    config[build_weight('space-outpost')] = { 200: ResourceSatisfied('Neutronium') == False }

    config[build_weight('space-living_quarters')] = 200
    config[build_weight('space-ziggurat')] = 150
    config[build_weight('space-red_mine')] = 102
    config[build_weight('space-fabrication')] = 101

    # Make space for living quarters
    with BuildingAffordable('space-living_quarters'):
        config[auto_build('space-red_mine')] = False
        config[auto_build('space-fabrication')] = False
        config[auto_build('space-biodome')] = False

    # Power generation priority
    with ResourceIncome('Power') < 5:
        config[build_weight('city-fission_power')] = 200

    # Building limits

    config[build_max('city-storage_yard')] = 12
    config[build_max('city-warehouse')] = 12
    config[build_max('city-silo')] = 10
    config[build_max('city-shed')] = 20
    config[build_max('city-lumber_yard')] = 20
    config[build_max('city-sawmill')] = 20
    config[build_max('city-rock_quarry')] = 20
    config[build_max('city-cement_plant')] = 20
    config[build_max('city-mine')] = 20
    config[build_max('city-coal_mine')] = 20
    config[build_max('city-oil_depot')] = 10
    config[build_max('city-oil_well')] = 10
    config[build_max('city-trade')] = 20
    config[build_max('city-wharf')] = 10
    config[build_max('city-mass_driver')] = {
        -1: ResearchComplete('tech-orichalcum_driver'),
        0: BuildingUnlocked('space-elerium_contain')
    }
    config[auto_build('space-swarm_plant')] = False
    config[auto_build('space-swarm_control')] = False
    config[auto_build('space-swarm_satellite')] = False
    config[auto_build('space-gps')] = False
    config[auto_build('space-drone')] = False
    config[auto_build('space-iron_ship')] = False
    config[auto_build('space-oil_extractor')] = False

    # Don't overbuild fuel depots
    mission_unaffordable = lambda mission: BuildingUnlocked(mission) & ~BuildingAffordable(mission)
    any_missions_unaffordable = any_of(mission_unaffordable(mission) for mission in SPACE_MISSIONS)
    config[auto_build('space-propellant_depot')] = any_missions_unaffordable
    config[auto_build('space-gas_storage')] = any_missions_unaffordable

    with ResetType('mad'):
        config[auto_build('city-hospital')] = False
        config[auto_build('city-boot_camp')] = False
        config[build_max('city-garrison')] = 20
        config[build_max('city-factory')] = 1

    with ResetType('bioseed'):
        config[auto_build('city-hospital')] = False
        config[auto_build('city-boot_camp')] = False
        config[build_max('city-garrison')] = 26
        config[build_max('space-red_mine')] = 1
        config[build_max('space-fabrication')] = 1
        config[auto_build('space-biodome')] = False
        config[build_max('space-space_station')] = 2
        config[build_max('space-elerium_ship')] = 2
        config[build_max('space-elerium_contain')] = 1

        # Keep building biolabs to speed up sequencing
        with BuildingUnlocked('space-star_dock') == False:
            config[auto_build('city-biolab')] = True
            # No need for more knowledge multiplies the weight by 0.01, so counteract that
            config[build_weight('city-biolab')] = { 10000: ResourceSatisfied('Knowledge') }

        # Don't overbuild knowledge structs
        with ResearchComplete('tech-quantum_manufacturing'):
            config[auto_arpa('lhc')] = False
            config[auto_build('city-university')] = False
            config[auto_build('city-library')] = False
            config[auto_build('city-wardenclyffe')] = False
            config[auto_build('city-biolab')] = False
            config[auto_build('space-satellite')] = False
            config[auto_build('space-exotic_lab')] = False
            config[auto_build('space-observatory')] = False

    with ResetType('whitehole'):
        config[build_max('space-red_mine')] = 10
        config[build_max('space-fabrication')] = 10

    with ResetType('ascension'):
        config[build_max('space-red_mine')] = 20
        config[build_max('space-fabrication')] = 20
