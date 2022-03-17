''' Main interface to an ESDL energy system '''

# pylint: disable=no-member
import uuid

from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage, alias
from pyecore.notification import EObserver

from app.utils.exceptions import EnergysystemParseError
from app.utils.esdl import equal_or_in

from vendor.energy_system.xml_resource import XMLResource
# from vendor.esdl import esdl

from .StringURI import StringURI


class EnergySystemHandler:
    """Class to handle (load, read, and update) an ESDL Energy System"""

    # TODO: CAN WE USE THE THING FROM THE VENDOR MODULE?
    # TODO: extract this to a simple module (NO CLASS) and just import the (self.)esdl
    # somewhere and define all the lookup there - because the lookup does not need
    # this whole class right?? just the self.esdl and that has nothing to do with the
    # actual esdl??
    def __init__(self, name=None):
        # create a resourceSet that hold the contents of the esdl.ecore model and the
        # instances we use/create
        self.rset = ResourceSet()

        # Assign files with the .esdl extension to the XMLResource instead of default XMI
        self.rset.resource_factory['esdl'] = lambda uri: XMLResource(uri)

        # Read the esdl.ecore from the tmp folder
        esdl_model_resource = self.rset.get_resource(URI('vendor/esdl/esdl.ecore'))

        esdl_model = esdl_model_resource.contents[0]
        # print('Namespace: {}'.format(esdl_model.nsURI))
        self.rset.metamodel_registry[esdl_model.nsURI] = esdl_model

        # Create a dynamic model from the loaded esdl.ecore model, which we can use to
        # build Energy Systems
        self.esdl = DynamicEPackage(esdl_model)

        # fix python buildin 'from' that is also used in ProfileElement as attribute
        # use 'start' instead of 'from' when using a ProfileElement
        alias('start', self.esdl.ProfileElement.findEStructuralFeature('from'))

        # have a nice __repr__ for some ESDL classes when printing ESDL objects
        # (includes all Assets and EnergyAssets)
        # self.esdl.Item.python_class.__repr__ = lambda x: format_repr(x.name, x)
        self.esdl.Carrier.python_class.__repr__ = lambda x: format_repr(x.name, x)
        self.esdl.Geometry.python_class.__repr__ = lambda x: format_repr(x.name, x)
        self.esdl.QuantityAndUnitType.python_class.__repr__ = lambda x: format_repr(x.id, x)
        self.esdl.QuantityAndUnitReference.python_class.__repr__ = lambda x: format_repr('QuantityAndUnitReference', x)
        self.esdl.KPI.python_class.__repr__ = lambda x: format_repr(x.name, x)
        self.esdl.ProfileElement.python_class.__repr__ = lambda x: format_repr('ProfileElement', x)

        if name:
            self.name = name
            self.load_energy_system(name)

    @staticmethod
    def generate_uuid():
        ''' Creates a uuid: useful for generating unique IDs '''
        return str(uuid.uuid4())


    def load_energy_system(self, name):
        ''' Load an ESDL file '''
        self.resource = self.rset.get_resource(URI(name))
        self.es = self.resource.contents[0]


    def add_data_source(self, name, description):
        ''' Adds a data_source to the ESDL containing a name and description'''
        data_source = self.esdl.DataSource(id='data_source', name=name, description=description)
        self.es.dataSource = data_source


    def get_quantity_and_units(self):
        '''
        Returns quantity and units

        Add energy system information to the energy system if it is not there yet
        Energy System information can be used to globally define the quantity and units of this
        system, instead of defining them manually per KPI in each area: this fosters reuse
        (but is not necessary)
        '''
        if not self.get_by_id('energy_system_information') is None:
            return self.get_by_id('quantity_and_units')

        self.__add_energy_system_information()
        q_and_u = self.esdl.QuantityAndUnits(id='quantity_and_units')
        self.es.energySystemInformation.quantityAndUnits = q_and_u

        return q_and_u

    def __add_energy_system_information(self):
        '''Add Energy System Information'''
        esi = self.esdl.EnergySystemInformation(id='energy_system_information')
        self.es.energySystemInformation = esi


    def add_measures(self):
        ''' Add Measures object to Energy System '''
        # Create new Measures object
        measures = self.esdl.Measures(id='measures')
        self.es.instance[0].area.measures = measures


    def append_measure(self, measure):
        ''' Append measure to Measures object '''
        self.es.instance[0].area.measures.measure.append(measure)


    def append_asset_to_measure(self, measure, asset):
        ''' Append asset measure to Measures object '''
        measure.asset.append(asset)
        self.es.instance[0].area.measures.measure.append(measure)

    ######## KPIs ########

    def add_kpis(self):
        ''' Add KPIs object to Energy System '''
        # create new KPIs object
        kpis = self.esdl.KPIs(id='kpis', description='KPIs')
        self.es.instance[0].area.KPIs = kpis


    def create_kpi(self, kpi_type, kpi_id, name, q_and_u):
        ''' Create new KPI object '''
        return getattr(self.esdl, kpi_type)(
            id=kpi_id,
            name=name,
            quantityAndUnit=q_and_u
        )


    def add_kpi(self, kpi):
        ''' Add KPI to KPIs object '''
        self.es.instance[0].area.KPIs.kpi.append(kpi)


    def get_kpi_by_id(self, kpi_id):
        ''' Returns a specific KPI by id, see also get_by_id for a faster method '''
        for kpi in self.es.instance[0].area.KPIs.kpi:
            if kpi.id == kpi_id:
                return kpi

        return None


    def get_kpi_by_name(self, name):
        ''' Returns a specific KPI by name '''
        for kpi in self.es.instance[0].area.KPIs.kpi:
            if kpi.name == name:
                return kpi

        return None

    ######### LOOKUP ##########

    def get_by_id(self, object_id):
        '''
        Using this function you can query for objects by ID
        After loading an ESDL-file, all objects that have an ID defines are stored in
        resource.uuid_dict automatically
        Note: If you add things later to the resource, it won't be added automatically to
        this dictionary though. Use get_by_id_slow() for that
        '''
        if object_id in self.resource.uuid_dict:
            return self.resource.uuid_dict[object_id]

        return None


    def get_by_id_slow(self, object_id):
        '''
        This function iterates over all the contents of the Energy System and is much slower
        than get_by_id()
        '''
        for child in self.es.eAllContents():
            if hasattr(child, 'id') and child.id == object_id:
                return child

        return None

    def get_assets_of_type(self, esdl_type, area=None):
        '''Get a list of assets of a specific ESDL type in the specified area or asset'''
        assets = area.asset if not area is None else self.es.instance[0].area.asset
        esdl_asset = getattr(self.esdl, esdl_type)

        return [asset for asset in assets if isinstance(asset, esdl_asset)]

    def has_assets_of_type(self, esdl_type, area=None):
        ''' Boolean, see get_assets_of_type '''
        assets = area.asset if not area is None else self.es.instance[0].area.asset

        try:
            next((asset for asset in assets if isinstance(asset, getattr(self.esdl, esdl_type))))
            return True
        except StopIteration:
            return False

    def get_assets_of_type_and_attribute_value(self, esdl_type, area, attr, val):
        '''
        Returns a list of assets of a specific ESDL type in the specified area or asset
        filtered by a specified attribute-value combination

        Params:
            esdl_type (str): The type of asset
            area (esdl.Area): The area that contains the assets to be filtered
            attr (str): The attribute that should be evaluated
            val (str): The value that the attribute should have

        Returns:
            list[esdl.Asset]
        '''
        esdl_asset = getattr(self.esdl, esdl_type)

        return [asset for asset in area.asset
                if isinstance(asset, esdl_asset) and str(getattr(asset, attr)) == val]

    def has_assets_of_type_and_attribute_value(self, esdl_type, area, attr, val):
        '''
        Works like get_of_type_and_attribute_value, but only checks if the first item
        can be generated

        Params:
            esdl_type (str): The type of asset
            area (esdl.Area): The area that contains the assets to be filtered
            attr (str): The attribute that should be evaluated
            val (str): The value that the attribute should have

        Returns:
            bool
        '''
        try:
            next((asset for asset in area.asset
                if isinstance(asset, getattr(self.esdl, esdl_type))
                and str(getattr(asset, attr)) == val))
            return True
        except StopIteration:
            return False

    def get_potentials_of_type(self, esdl_type):
        ''' Get a list of potentials of a specific ESDL type in the main instance's area '''
        potentials = []

        for current_potential in self.es.instance[0].area.potential:
            if isinstance(current_potential, esdl_type):
                potentials.append(current_potential)
        return potentials

    def get_all_instances_of_type(self, esdl_type):
        '''
        Returns a generator of all assets or potentials of a specific type.
        Not only the ones defined in the main Instance's Area e.g. QuantityAndUnits can be
        defined in the KPI of an Area or in the EnergySystemInformation object this
        function returns all of them at once.

        Params:
            esdl_type (str): The type of asset

        Returns:
            generator of assets or potentials
        '''
        yield from getattr(self.esdl, esdl_type).allInstances(resources=(self.resource,))

    def get_all_instances_of_type_and_attribute_value(self, esdl_type, attr, val):
        '''
        Returns a generator of all assets or potentials of a specific type.
        Not only the ones defined in the main Instance's Area e.g. QuantityAndUnits can be
        defined in the KPI of an Area or in the EnergySystemInformation object this
        function returns all of them at once.

        The assets are then filtered for a specific attribute-value combination

        Params:
            esdl_type (str): The type of asset
            attr (str): The attribute that should be evaluated
            val (str): The value that the attribute should have

        Returns:
            generator of assets or potentials
        '''
        yield from (inst for inst in self.get_all_instances_of_type(esdl_type)
                if str(getattr(inst, attr)) == val)

    def get_all_instances_of_type_and_sector(self, esdl_type, sector_id):
        '''
        Returns a generator of all assets or potentials of a specific type.
        Not only the ones defined in the main Instance's Area e.g. QuantityAndUnits can be
        defined in the KPI of an Area or in the EnergySystemInformation object this
        function returns all of them at once.

        The assets are then filtered for a specific combination on an attribute and it's ID.

        Params:
            esdl_type (str): The type of asset
            sector_id (str | list[str]): The value of the sectors id, e.g. REF for Refineries

        Returns:
            generator of assets or potentials
        '''
        yield from (inst for inst in self.get_all_instances_of_type(esdl_type)
                if self.in_sector(inst, sector_id))

    def get_all_instances_of_type_and_carrier(self, esdl_type, carrier_id):
        '''
        Returns a generator of all assets or potentials of a specific type.
        Not only the ones defined in the main Instance's Area e.g. QuantityAndUnits can be
        defined in the KPI of an Area or in the EnergySystemInformation object this
        function returns all of them at once.

        The assets are then filtered for having the specified carrier as input.

        Params:
            esdl_type (str): The type of asset
            carrier_id (str | list[str]): The value of the carriers id, e.g. HTLH for network gas

        Returns:
            generator of assets or potentials
        '''
        yield from (inst for inst in self.get_all_instances_of_type(esdl_type)
                if self.has_carrier(inst, carrier_id))

    def get_all_instances_of_type_carrier_and_sector(self, esdl_type, sector_id, carrier_id):
        '''
        Returns a generator of all assets or potentials of a specific type.
        Not only the ones defined in the main Instance's Area e.g. QuantityAndUnits can be
        defined in the KPI of an Area or in the EnergySystemInformation object this
        function returns all of them at once.

        The assets are then filtered for given sectors and carriers.

        Params:
            esdl_type (str): The type of asset
            sector_id (str | list[str]): The value of the sectors id, e.g. REF for Refineries
            carrier_id (str | list[str]): The value of the carriers id, e.g. HTLH for network gas

        Returns:
            generator of assets or potentials
        '''
        yield from (inst for inst in self.get_all_instances_of_type(esdl_type)
                if self.in_sector(inst, sector_id) and self.has_carrier(inst, carrier_id))

    def has_carrier(self, asset, carrier_id):
        '''Carrier id may also be a list'''
        for port in asset.port:
            if not isinstance(port, self.esdl.InPort): continue

            if port.carrier.id == carrier_id:
                return True

            if isinstance(carrier_id, list) and port.carrier.id in carrier_id:
                return True

        return False

    def in_sector(self, asset, sector_id):
        '''
        Returns Boolean depending on if the asset is in the sector or not. Also checks if the assets
        parents have a sector set, if 'sector' is not an attribute of the asset directly.

        Params:
            asset (pyecore.ecore.Object): The asset that is to be checked.
            sector_id (str | list[str]): The id of the sector, e.g. REF for Refineries.

        Returns:
            bool
        '''
        if asset.sector and equal_or_in(asset.sector.id, sector_id):
            return True

        for port in asset.port:
            if not isinstance(port, self.esdl.OutPort): continue

            for connection in port.connectedTo:
                if not getattr(connection.energyasset, 'sector', None): continue

                if equal_or_in(connection.energyasset.sector.id, sector_id):
                    return True

        return False


    def get_asset_attribute(self, esdl_type, attr, area=None):
        '''
        Create a readable list of the attributes of an ESDL class
        Scoped to a specific area, if one is given

        Returns:
            list[dict] with formatted assets
        '''
        assets = area.asset if not area is None else self.es.instance[0].area.asset

        return [self.__format_asset(ass, attr) for ass in assets if isinstance(ass, esdl_type)]


    def __format_asset(self, current_asset, attribute):
        return {
            'name': current_asset.name,  # name
            'attribute': {
                'key': attribute,
                'value': getattr(current_asset, attribute)
            }
        }

    ######### LOAD & SAVE ##########

    def save(self, filename):
        ''' Saves the energy system to a file '''
        uri = URI(filename)
        fileresource = self.rset.create_resource(uri)
        # add the current energy system
        fileresource.append(self.es)
        # save the resource
        fileresource.save()
        # return the resource
        return fileresource


    def get_as_string(self):
        '''
        Returns the current energy system as an XML string

        Note: does not change the 'active' resource so save() will still save as a file
        '''
        # to use strings as resources, we simulate a string as being a file
        uri = StringURI('tmp/anyname.esdl')
        # create the string resource
        stringresource = self.rset.create_resource(uri)
        # add the current energy system
        stringresource.append(self.es)
        # save the resource
        stringresource.save()
        # remove the temporary resource in the resource set
        self.rset.remove_resource(stringresource)
        # return the string
        return uri.getvalue()


    def get_as_stream(self):
        '''
        Returns the current energy system as a BytesIO stream
        '''
        # to use strings as resources, we simulate a string as being a file
        uri = StringURI('tmp/anyname.esdl')
        # create the string resource
        stringresource = self.rset.create_resource(uri)
        # add the current energy system
        stringresource.append(self.es)
        # save the resource
        stringresource.save()
        # remove the temporary resource in the resource set
        self.rset.remove_resource(stringresource)
        # return the string
        return uri.get_stream()

    @classmethod
    def from_string(cls, esdl_string):
        '''
        Create a new EnergySystemHandler based on an EnergySystem esdl_string (using UTF-8 encoding)
        '''
        try:
            handler = EnergySystemHandler()
            handler.resource = handler.rset.create_resource(
                StringURI('loadfromstring', esdl_string)
            )
            handler.resource.load()
            handler.es = handler.resource.contents[0]
            return handler
        except Exception as exception:
            raise EnergysystemParseError('ESDL could not be parsed') from exception


def format_repr(name, esdl_object):
    ''' Returns a string containing a formatted version of the ESDL object'''
    return f'{name}: ({attr_to_dict(esdl_object)})'


def attr_to_dict(esdl_object):
    ''' Creates a dict of all the attributes of an ESDL object '''
    to_dict = dict()
    to_dict['esdlType'] = esdl_object.eClass.name
    for attr in dir(esdl_object):
        attr_value = esdl_object.eGet(attr)
        if attr_value is not None:
            to_dict[attr] = attr_value
    return to_dict


class PrintNotification(EObserver):
    ''' Custom observer that prints notifications'''
    def __init__(self, notifier=None):
        super().__init__(notifier=notifier)

    def notifyChanged(self, notification):
        print('Notification: {}'.format(notification))