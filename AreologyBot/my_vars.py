import sc2
from sc2.constants import *
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID

class my_vars:
    def __init__(self):
        self.initialize_unit_groups()
        self.initialize_units_types()

    def initialize_unit_groups(self):
        """Initialize our unit types"""
        self.drones = self.units(UnitID.DRONE)
        self.larvae = self.units(UnitID.LARVA)
        self.queens = self.units(UnitID.QUEEN)
        self.ground_army = self.units.filter(lambda unit: unit.type_id in {UnitID.ZERGLING, UnitID.BANELING})
        self.air_army = self.units.filter(lambda unit: unit.type_id in {UnitID.MUTALISK, UnitID.OVERSEER})

    def initialize_units_types(self):
        """Initialize our units"""
        self.actualOverlordCount =      self.units(UnitID.OVERLORD).amount + self.already_pending(UnitID.OVERLORD)
        self.actualQueenCount =         self.units(UnitID.QUEEN).amount + self.already_pending(UnitID.QUEEN)
        self.actualZerglingPairCount =  self.units(UnitID.ZERGLING).amount + self.already_pending(UnitID.ZERGLING)
        self.actualRoachCount =         self.units(UnitID.ROACH).amount + self.already_pending(UnitID.ROACH)
        self.actualHydraliskCount =     self.units(UnitID.HYDRALISK).amount + self.already_pending(UnitID.HYDRALISK)
        self.actualCorruptorCount =     self.units(UnitID.CORRUPTOR).amount + self.already_pending(UnitID.CORRUPTOR)
        self.actualBroodlordCount =     self.units(UnitID.BROODLORD).amount + self.units(UnitID.BROODLORDCOCOON).amount

        # Worker Supply (existing + in production + in gas)
        self.actualDroneSupply = self.units(UnitID.DRONE).amount + self.already_pending(UnitID.DRONE) + self.units(UnitID.EXTRACTOR).ready.filter(lambda x:x.vespene_contents > 0).amount
        # Army Supply (Food supply of all units except Drones and Overlords)
        self.actualArmySupply = 2 * self.actualQueenCount + 1 * self.actualZerglingPairCount + 2 * self.actualRoachCount + 2 * self.actualHydraliskCount + 2 * self.actualCorruptorCount + 4 * self.actualBroodlordCount
