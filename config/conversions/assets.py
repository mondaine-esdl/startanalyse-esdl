'''
Config for the mapping of assets in ESDL and their ETM counterparts
'''

ASSETS = [
     ### HeatingDemand ##
    {
        'asset': 'HeatingDemand',
        'parser': 'volume',
        'attribute': 'power',
        'sector': 'REF',
        'input': 'industry_useful_demand_for_chemical_refineries',
        'factor': 1E-6
    }, # CHEMFEED, EDOIL and NONCHLO should be taken into account together
    {
        'asset': 'HeatingDemand',
        'parser': 'volume',
        'attribute': 'power',
        'sector': 'CHEMFEED',
        'input': 'industry_useful_demand_for_chemical_other',
        'factor': 1E-6
    }, # CHEMFEED, EDOIL and NONCHLO should be taken into account together
    {
        'asset': 'HeatingDemand',
        'parser': 'volume',
        'attribute': 'power',
        'sector': 'EDOIL',
        'input': 'industry_useful_demand_for_chemical_other',
        'factor': 1E-6
    },  # CHEMFEED, EDOIL and NONCHLO should be taken into account together
    {
        'asset': 'HeatingDemand',
        'parser': 'volume',
        'attribute': 'power',
        'sector': 'NONCHLO',
        'input': 'industry_useful_demand_for_chemical_other',
        'factor': 1E-6
    },

    ### WindTurbine ###
    {
        'asset': 'WindTurbine',
        'parser': 'volatile',
        'attr_set': { # Volatile has sets of attributes, one power and one flh
            'power': {
                'input': 'capacity_of_energy_power_wind_turbine_inland',
                'gquery': 'merit_order_onshore_wind_turbines_capacity_in_merit_order_table',
                'factor': 1E-6,
                'edr': 'b68cb054-44ee-46cb-a32b-ef1b7830f0e1'
            },
            'fullLoadHours': {
                'input': 'flh_of_energy_power_wind_turbine_inland',
                'gquery': 'merit_order_onshore_wind_turbines_full_load_hours_in_merit_order_table',
                'factor': 1,
                'edr': 'b68cb054-44ee-46cb-a32b-ef1b7830f0e1'
            }
        }
    },

    ### PVPark ###
    {
        'asset': 'PVPark',
        'parser': 'volatile',
        'attr_set': { # Volatile has sets of attributes, one power and one flh
            'power': {
                'input': 'capacity_of_energy_power_solar_pv_solar_radiation',
                'gquery': '',
                'factor': 1E-6,
                'edr': ''
            },
            'fullLoadHours': {
                'input': 'flh_of_solar_pv_solar_radiation',
                'gquery': '',
                'factor': 1,
                'edr': ''
            }
        },
    },

    ### Rooftop PV ###
    {
        'asset': 'RooftopPV',
        'parser': 'rooftop_pv',
        'inputs': {
            'RESIDENTIAL': 'households_solar_pv_solar_radiation_market_penetration',
            'BUILDINGS': 'buildings_solar_pv_solar_radiation_market_penetration'
        },
        'factor': 1E2
    },

    ### CHPs ###
    {
        'asset': 'CHP',
        'parser': 'subtype_capacity',
        'attribute': 'power',
        'type_key': 'CHPType',
        'type': 'UNDEFINED', # do we want to support this?
        'input': 'capacity_of_industry_chp_combined_cycle_gas_power_fuelmix',
        'factor': 1E-6
    },
    {
        'asset': 'CHP',
        'parser': 'subtype_capacity',
        'attribute': 'power',
        'type_key': 'CHPType',
        'type': 'STEG',
        'input': 'capacity_of_industry_chp_combined_cycle_gas_power_fuelmix',
        'factor': 1E-6
    },
    {
        'asset': 'CHP',
        'parser': 'subtype_capacity',
        'attribute': 'power',
        'type_key': 'CHPType',
        'type': 'GAS_TURBINE',
        'input': 'capacity_of_industry_chp_turbine_gas_power_fuelmix',
        'factor': 1E-6
    },
    {
        'asset': 'CHP',
        'parser': 'subtype_capacity',
        'attribute': 'power',
        'type_key': 'CHPType',
        'type': 'GAS_MOTOR',
        'input': 'capacity_of_industry_chp_engine_gas_power_fuelmix',
        'factor': 1E-6
    },
    {
        'asset': 'CHP',
        'parser': 'volume',
        'attribute': 'power',
        'sector': 'REF',
        'input': 'industry_final_demand_for_chemical_other_steam_hot_water_share',
        'factor': 1E-6
    },

    ### GasHeaters ###
    {
        'asset': 'GasHeater',
        'parser': 'carrier_volume',
        'attribute': 'power',
        'carrier': ['HTLH', 'RTLH_ODO', 'RTLH_NODO'],
        'sector': 'REF',
        'input': 'industry_chemicals_other_burner_network_gas_share',
        'factor': 1E-6
    },
    {
        'asset': 'GasHeater',
        'parser': 'carrier_volume',
        'attribute': 'power',
        'carrier': ['RG', 'PC'],
        'sector': 'REF',
        'input': 'industry_chemicals_other_burner_crude_oil_share',
        'factor': 1E-6
    },
    {
        'asset': 'GasHeater',
        'parser': 'carrier_volume',
        'attribute': 'power',
        'carrier': ['H2_local', 'H2_Hvision', 'H2_new'],
        'sector': 'REF',
        'input': 'industry_chemicals_other_burner_hydrogen_share',
        'factor': 1E-6
    },

    ### BiomassHeaters ###
    {
        'asset': 'BiomassHeater',
        'parser': 'carrier_volume',
        'attribute': 'power',
        'carrier': 'BM',
        'sector': 'REF',
        'input': 'industry_chemicals_other_burner_wood_pellets_share',
        'factor': 1E-6
    },

    ### HeatPumps ###
    {
        'asset': 'HeatPump',
        'parser': 'carrier_volume',
        'attribute': 'power',
        'carrier': 'E',
        'sector': 'REF',
        'input': 'industry_chemicals_other_heater_electricity_share',
        'factor': 1E-6
    },

    ### PowerPlants ###
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'HTLH',
        'input': 'capacity_of_energy_power_combined_cycle_network_gas',
        'factor': 1E-6
    },
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'RG',
        'input': 'capacity_of_energy_power_combined_cycle_network_gas',
        'factor': 1E-6
    },
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'PC',
        'input': 'capacity_of_energy_power_ultra_supercritical_coal',
        'factor': 1E-6
    },
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'RF',
        'input': 'capacity_of_energy_power_ultra_supercritical_coal',
        'factor': 1E-6
    },
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'W',
        'input': 'capacity_of_energy_power_supercritical_waste_mix',
        'factor': 1E-6
    },
    {
        'asset': 'PowerPlant',
        'parser': 'carrier_capacity',
        'attribute': 'power',
        'carrier': 'C',
        'input': 'capacity_of_energy_power_ultra_supercritical_coal',
        'factor': 1E-6
    }
]

distributions = {
    'energyLabelDistribution': {
        'category': 'labelPerc',
        'attribute': 'energyLabel',
        'percentage': 'percentage',
        'inputs': {
            'RESIDENTIAL': [
                'households_insulation_level_apartments',
                'households_insulation_level_corner_houses',
                'households_insulation_level_detached_houses',
                'households_insulation_level_semi_detached_houses',
                'households_insulation_level_terraced_houses',
            ],
            'UTILITY': [
                'buildings_insulation_level'
            ]
        }
    }
}

heating_technologies = {
    'HeatPump': [
        { # Hybride warmtepomp op methaan
            'attribute': 'additionalHeatingSourceType',
            'value': 'GAS',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_hybrid_heatpump_air_water_electricity_share',
                'UTILITY': 'buildings_space_heater_heatpump_air_water_network_gas_share'
            },
            'aggregation': 'sum'
        },
        { # Hybride warmtepomp op waterstof
            'attribute': 'additionalHeatingSourceType',
            'value': 'HYDROGEN',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_hybrid_hydrogen_heatpump_air_water_electricity_share',
                'UTILITY': 'buildings_space_heater_heatpump_air_water_network_gas_share'
            },
            'aggregation': 'sum'
        },
        { # Elektrische luchtwarmtepomp
            'attribute': 'source',
            'value': 'AIR',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_heatpump_air_water_electricity_share',
                'UTILITY': 'buildings_space_heater_collective_heatpump_water_water_ts_electricity_share'
            },
            'aggregation': 'sum'
        },
        { # Elektrische bodemwarmtepomp
            'attribute': 'source',
            'value': 'AQUIFER',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_heatpump_ground_water_electricity_share',
                'UTILITY': 'buildings_space_heater_collective_heatpump_water_water_ts_electricity_share'
            },
            'aggregation': 'sum'
        },
        { # Elektrische bodemwarmtepomp
            'attribute': 'source',
            'value': 'SUB_SURFACE',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_heatpump_ground_water_electricity_share',
                'UTILITY': 'buildings_space_heater_collective_heatpump_water_water_ts_electricity_share'
            },
            'aggregation': 'sum'
        }
    ],
    'HConnection': [
        { # Aansluiting op het warmtenet
            'attribute': '',
            'value': '',
            'inputs': { # dependent on building types
                'RESIDENTIAL': 'households_heater_district_heating_steam_hot_water_share',
                'UTILITY': 'buildings_space_heater_district_heating_steam_hot_water_share'
            },
            'aggregation': 'sum'
        }
    ],
    'GasHeater': [
        { # CV-ketel
            'attribute': '',
            'value': '',
            'inputs': { #dependent on building types
                'RESIDENTIAL': 'households_heater_combined_network_gas_share',
                'UTILITY': 'buildings_space_heater_network_gas_share'
            },
            'aggregation': 'sum'
        }
    ]
}
