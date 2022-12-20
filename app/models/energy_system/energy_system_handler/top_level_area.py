#  Methods to check for, and insert a top level area into the ESDL
import esdl
import copy

def is_top_area(self, area_name):
    '''Returns True if the area is the top area of the ESDL'''
    return self.area().name == area_name

def add_top_level_area(self, area_name):
    '''Inserts a top level area with the area name'''
    instance = self.get_energy_system().instance[0]

    top_area = esdl.Area(name=area_name)
    old_area = copy.deepcopy(self.area())
    instance.area = top_area
    old_area.containingArea = top_area
