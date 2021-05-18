''' Represents a single supply asset '''

from app.models.energy_system import EnergyDataRepository
from app.helpers.exceptions import EnergysystemParseError
from app.services.query_scenario import QueryScenario

class Supply():
    """
    Class to parse ESDL information about a single supply asset and
    translate it to the relevant ETM inputs.
    """

    def __init__(self, energy_system, asset_type, props):
        self.energy_system = energy_system
        self.asset_type = asset_type
        self.props = props
        self.list_of_assets = []
        self.power = 0.
        self.full_load_hours = 0.


    def parse(self):
        """
        Check the power and full load hours to set the corresponding props.
        Returns a dict containing ETM inputs that can be used when converting ESDL to
        slider settings.
        """
        self.all_instances()
        return self.set_props()


    def update(self, scenario_id):
        """
        Update the power and full load hours based on the ETM inputs
        """
        self.parse()
        self.update_props(scenario_id)


    def all_instances(self):
        """
        Get all instances of asset type and return as a list.
        """
        try:
            self.list_of_assets = self.energy_system.get_all_instances_of_type(
                getattr(self.energy_system.esdl, self.asset_type))

        except AttributeError as att:
            raise EnergysystemParseError(
                f'We currently do not support the asset {str(att).split()[-1]}'
            ) from att

    def set_props(self):
        """
        Check the total power of the given asset

        Returns a dict of ETM inputs and their new values
        """
        total_power = 0.
        full_load_hours = 0.

        inputs = {}

        for asset in self.list_of_assets:
            for prop in self.props:
                # Calculate ETM input value
                esdl_value = getattr(asset, prop['attribute'])
                etm_value = esdl_value * prop['factor']

                # Initialise the input value if it hasn't been touched yet
                if not prop['input'] in inputs:
                    inputs[prop['input']] = 0

                # Keep track of the installed capacity to determine the average FLH
                if prop['attribute'] == 'power':
                    current_power = etm_value
                    total_power += etm_value
                    # print(f'CAP = {total_power}')

                elif prop['attribute'] == 'fullLoadHours':
                    prev_etm_value = inputs[prop['input']]
                    diff = etm_value - prev_etm_value # 1920 - 2500 = -580
                    etm_value = diff * current_power / total_power # -580 * 13 / 19
                    full_load_hours += etm_value
                    # print(f'FLH = {full_load_hours}')

                # Update ETM input value
                inputs[prop['input']] += etm_value

            self.power = total_power
            self.full_load_hours = full_load_hours

        print(f'self.power = {self.power}')
        print(f'self.full_load_hours = {self.full_load_hours}')

        return inputs


    def query_scenario(self, scenario_id, prop):
        """
        TODO
        """
        query_result = QueryScenario.execute(scenario_id, prop['gquery'])

        if query_result.successful:
            return query_result.value[prop['gquery']]['future'] / prop['factor']

        raise EnergysystemParseError(
            f"We currently do not support the ETM gquery listed in the config: {prop['gquery']}"
        )


    def update_props(self, scenario_id):
        """
        TODO
        """
        list_of_props = {}
        for prop in self.props:
            list_of_props[prop['attribute']] = prop

        # First, update the full load hours. This value is necessary for the
        # measures that follow from updating the power.
        # TODO: Send the queries in batches instead of one-by-one
        for attr in ['fullLoadHours', 'power']:
            prop = list_of_props[attr]
            val = self.query_scenario(scenario_id, prop)

            if attr == 'fullLoadHours':
                self.update_flh(val / prop['factor'])

            elif attr == 'power':
                diff = val - (self.power / prop['factor'])
                if diff > 0:
                    self.add_measures(diff, prop['edr'])
                elif diff < 0:
                    pass
                    # self.remove_assets(diff)


    def update_flh(self, val):
        """
        For each instance in the list of assets of this type of supply, update
        the number of full load hours to the ETM value.
        """
        self.full_load_hours = val

        for asset in self.list_of_assets:
            asset.fullLoadHours = val


    def remove_assets(self, diff):
        """
        Update the installed capacity of wind turbines based on the ETM value.
        If the capacity has decreased, remove redundant assets. If it has
        increased, don't touch the assets but add measure to the ESDL energy
        system.
        """
        remaining_diff = diff
        while remaining_diff > 0:
            asset = self.list_of_assets[0]
            if asset.power > remaining_diff:
                asset.power = asset.power - remaining_diff
                break
            remaining_diff -= asset.power
            self.list_of_assets.remove(asset)
            # TODO: It's probably necessary to remove the actual asset in the
            # energy system instead of the copy in this list (by using the id?)


    def add_measures(self, diff, asset_id):
        """
        WIP (test scenario 806669): 26 MW onshore wind
        """
        self.energy_system.add_measures()

        edr = EnergyDataRepository()
        edr_asset = edr.get_asset(asset_id)

        power = edr_asset.power
        flh = int(self.full_load_hours)

        measure = self.energy_system.esdl.Measure()

        # klass = getattr(self.energy_system.esdl, self.asset_type)
        # constructor = globals()[klass.name]

        remaining_diff = diff
        while remaining_diff > 0:
            # asset = constructor()
            if power > remaining_diff:
                power = remaining_diff

            asset = self.energy_system.esdl.WindTurbine(
                id=self.energy_system.generate_uuid(),
                power=power,
                fullLoadHours=flh)

            self.energy_system.append_asset_to_measure(measure, asset)

            remaining_diff -= asset.power
