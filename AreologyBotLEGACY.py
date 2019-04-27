import random
import math

from sc2.unit import *
from sc2.units import *
from sc2.data import *

import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.ids.ability_id import *
from sc2.ids.unit_typeid import *
from sc2.ids.upgrade_id import *
from sc2.position import Point2, Point3
from sc2.player import Bot, Computer, Human

# Custom Imports
# from AreologyBot import TestFile

# note: self.townhalls.amount = number of hatcheries + lairs + hives
# note: foo.exists (can be buildling)
# note: bar.ready (is already finished)

""" ### To do-List [Ctrl + f "###" to see problematic places]
Implement Scouting
Implement Early game defense
Implement Immediate gas saturation
Implement Creep spread (and tumor placement)
Implement Proper army manipulation (army distribution), don't just have them patrol
Implement Anti cloak measues
Implement Check all enemy bases
Implement Proper extractor production (ERRORS)
Implement Overseer logic (builds way too many)
Implement Burrow Micro
Implement No conga line all attack

Implement army pull back after traveling X distance away from bases, so they don't funnel into opponent's bases
Implement queen pull back after X % creep spread, so they don't die spreading creep on opponent's side of the map

Learn about hasattr(object, key)

Need to fix Evolution Chamber upgrade logic (sometimes 2nd evo doesn't upgrade)
"""
class AreologyBot(sc2.BotAI):
    def __init__(self):

        self.partneredQueens = {} # Used for Injecting

        # major events
        self.greaterspireStarted = False
        self.burrowUpgradeStarted = False

        self.enableArmyProduction = []
        self.enableDroneProduction = []
        self.enableQueenProduction = []

        self.stopMakingNewTumorsWhenAtCoverage = 0.3
        self.creepTargetDistance = 15
        self.creepTargetCountsAsReachedDistance = 10

        self.lairStarted = False
        self.hiveStarted = False


    # Total time elapsed (in minutes)
    def minutesElapsed(self):
        return self.time / 60
    """""""""""""""
      QUEEN MACRO
         STUFF
    """""""""""""""
    def partnerQueen(self, maxAmountInjectQueens = 5):
        # list of all alive queens and bases, will be used for injecting
        if not hasattr(self, "partneredQueens") or maxAmountInjectQueens == 0:
            self.partneredQueens = {}

        # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
        queensNoInjectPartner = self.units(QUEEN).filter(lambda q: q.tag not in self.partneredQueens.keys())
        basesNoInjectPartner = self.townhalls.filter(lambda h: h.tag not in self.partneredQueens.values() and h.build_progress > 0.8)

        # Assigns a Queen to nearest townhall without a Queen partner
        for queen in queensNoInjectPartner:
            if basesNoInjectPartner.amount == 0:
                break
            closestBase = basesNoInjectPartner.closest_to(queen)
            self.partneredQueens[queen.tag] = closestBase.tag
            basesNoInjectPartner = basesNoInjectPartner - [closestBase]
            break

    async def doQueenInjects(self, iteration):
        # list of all alive queens and bases, will be used for injecting
        queenAliveTag = [queen.tag for queen in self.units(QUEEN)] # list of numbers (tags / unit IDs)
        townhallAliveTag = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        toRemoveTags = []

        if hasattr(self, "partneredQueens"):
            for specificQueenTag, specificTownhallTag in self.partneredQueens.items():
                # Remove Tag if Queen is no longer alive
                if specificQueenTag not in queenAliveTag:
                    toRemoveTags.append(specificQueenTag)
                    continue
                # Remove Tag if townhall is no longer alive
                if specificTownhallTag not in townhallAliveTag:
                    toRemoveTags.append(specificQueenTag)
                    continue
                # Queen injects Hatchery if both are alive and Queen has at least 25 energy
                queen = self.units(QUEEN).find_by_tag(specificQueenTag)
                hatch = self.townhalls.find_by_tag(specificTownhallTag)
                if hatch.is_ready:
                    if queen.energy >= 25 and queen.is_idle and not hatch.has_buff(QUEENSPAWNLARVATIMER):
                        await self.do(queen(EFFECT_INJECTLARVA, hatch))
            # Remove Queen Tags in case either Queen or townhall is destroyed
            # Note: Outside of loop in order to reset every tag
            for tag in toRemoveTags:
                self.partneredQueens.pop(tag)
    """""""""""""""
      CREEP STUFF
    """""""""""""""
    async def findCreepPlantLocation(self, targetPositions, castingUnit, minRange=None, maxRange=None, stepSize=1, onlyAttemptPositionsAroundUnit=False, locationAmount=32, dontPlaceTumorsOnExpansions=True):
        assert isinstance(castingUnit, Unit)
        positions = []
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]
        if minRange is None: minRange = 0
        if maxRange is None: maxRange = 500

        # get positions around the casting unit
        positions = self.getPositionsAroundUnit(castingUnit, minRange=minRange, maxRange=maxRange, stepSize=stepSize, locationAmount=locationAmount)

        # stop when map is full with creep
        if len(self.positionsWithoutCreep) == 0:
            return None

        # filter positions that would block expansions
        if dontPlaceTumorsOnExpansions and hasattr(self, "exactExpansionLocations"):
            positions = [x for x in positions if self.getHighestDistance(x.closest(self.exactExpansionLocations), x) > 3]
            # TODO: need to check if this doesnt have to be 6 actually
            # this number cant also be too big or else creep tumors wont be placed near mineral fields where they can actually be placed

        # check if any of the positions are valid
        validPlacements = await self._client.query_building_placement(ability, positions)

        # filter valid results
        validPlacements = [p for index, p in enumerate(positions) if validPlacements[index] == ActionResult.Success]

        allTumors = self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(CREEPTUMORQUEEN)
        # usedTumors = allTumors.filter(lambda x:x.tag in self.usedCreepTumors)
        unusedTumors = allTumors.filter(lambda x:x.tag not in self.usedCreepTumors)
        if castingUnit is not None and castingUnit in allTumors:
            unusedTumors = unusedTumors.filter(lambda x:x.tag != castingUnit.tag)

        # filter placements that are close to other unused tumors
        if len(unusedTumors) > 0:
            validPlacements = [x for x in validPlacements if x.distance_to(unusedTumors.closest_to(x)) >= 10]

        validPlacements.sort(key=lambda x: x.distance_to(x.closest(self.positionsWithoutCreep)), reverse=False)

        if len(validPlacements) > 0:
            return validPlacements
        return None

    def getPositionsAroundUnit(self, unit, minRange=0, maxRange=500, stepSize=1, locationAmount=32):
        # e.g. locationAmount=4 would only consider 4 points: north, west, east, south
        assert isinstance(unit, (Unit, Point2, Point3))
        if isinstance(unit, Unit):
            loc = unit.position.to2
        else:
            loc = unit
        positions = [Point2(( \
            loc.x + distance * math.cos(math.pi * 2 * alpha / locationAmount), \
            loc.y + distance * math.sin(math.pi * 2 * alpha / locationAmount))) \
            for alpha in range(locationAmount) # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
            for distance in range(minRange, maxRange+1)] # distance depending on minrange and maxrange
        return positions

    async def updateCreepCoverage(self, stepSize=None):
        if stepSize is None:
            stepSize = self.creepTargetDistance
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]

        positions = [Point2((x, y)) \
        for x in range(self._game_info.playable_area[0]+stepSize, self._game_info.playable_area[0] + self._game_info.playable_area[2]-stepSize, stepSize) \
        for y in range(self._game_info.playable_area[1]+stepSize, self._game_info.playable_area[1] + self._game_info.playable_area[3]-stepSize, stepSize)]

        validPlacements = await self._client.query_building_placement(ability, positions)
        successResults = [
            ActionResult.Success, # tumor can be placed there, so there must be creep
            ActionResult.CantBuildLocationInvalid, # location is used up by another building or doodad,
            ActionResult.CantBuildTooFarFromCreepSource, # - just outside of range of creep
            # ActionResult.CantSeeBuildLocation - no vision here
            ]
        # self.positionsWithCreep = [p for index, p in enumerate(positions) if validPlacements[index] in successResults]
        self.positionsWithCreep = [p for valid, p in zip(validPlacements, positions) if valid in successResults]
        self.positionsWithoutCreep = [p for index, p in enumerate(positions) if validPlacements[index] not in successResults]
        self.positionsWithoutCreep = [p for valid, p in zip(validPlacements, positions) if valid not in successResults]
        return self.positionsWithCreep, self.positionsWithoutCreep

    async def spreadCreep(self):
        # only use queens that are not assigned to do larva injects
        allTumors = self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(CREEPTUMORQUEEN)

        if not hasattr(self, "usedCreepTumors"):
            self.usedCreepTumors = set()

        # gather all queens that are not assigned for injecting and have 25+ energy
        if hasattr(self, "partneredQueens"):
            unassignedQueens = self.units(QUEEN).filter(lambda q: (q.tag not in self.partneredQueens and q.energy >= 25 or q.energy >= 50) and (q.is_idle or len(q.orders) == 1 and q.orders[0].ability.id in [AbilityId.MOVE]))
        else:
            unassignedQueens = self.units(QUEEN).filter(lambda q: q.energy >= 25 and (q.is_idle or len(q.orders) == 1 and q.orders[0].ability.id in [AbilityId.MOVE]))

        # update creep coverage data and points where creep still needs to go
        if not hasattr(self, "positionsWithCreep"):
            posWithCreep, posWithoutCreep = await self.updateCreepCoverage()
            totalPositions = len(posWithCreep) + len(posWithoutCreep)
            self.creepCoverage = len(posWithCreep) / totalPositions
            # print(self.getTimeInSeconds(), "creep coverage:", creepCoverage)

        # filter out points that have already tumors / bases near them
        if hasattr(self, "positionsWithoutCreep"):
            self.positionsWithoutCreep = [x for x in self.positionsWithoutCreep if (allTumors | self.townhalls).closer_than(self.creepTargetCountsAsReachedDistance, x).amount < 1 or (allTumors | self.townhalls).closer_than(self.creepTargetCountsAsReachedDistance + 10, x).amount < 5] # have to set this to some values or creep tumors will clump up in corners trying to get to a point they cant reach

        # make all available queens spread creep until creep coverage is reached 50%
        if hasattr(self, "creepCoverage") and (self.creepCoverage < self.stopMakingNewTumorsWhenAtCoverage or allTumors.amount - len(self.usedCreepTumors) < 25):
            for queen in unassignedQueens:
                # locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=queen, minRange=3, maxRange=30, stepSize=2, locationAmount=16)
                if self.townhalls.ready.exists:
                    locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=queen, minRange=3, maxRange=30, stepSize=2, locationAmount=16)
                    # locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=self.townhalls.ready.random, minRange=3, maxRange=30, stepSize=2, locationAmount=16)
                    if locations is not None:
                        for loc in locations:
                            err = await self.do(queen(BUILD_CREEPTUMOR_QUEEN, loc))
                            if not err:
                                break

        unusedTumors = allTumors.filter(lambda x: x.tag not in self.usedCreepTumors)
        tumorsMadeTumorPositions = set()
        for tumor in unusedTumors:
            tumorsCloseToTumor = [x for x in tumorsMadeTumorPositions if tumor.distance_to(Point2(x)) < 8]
            if len(tumorsCloseToTumor) > 0:
                continue
            abilities = await self.get_available_abilities(tumor)
            if AbilityId.BUILD_CREEPTUMOR_TUMOR in abilities:
                locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=tumor, minRange=10, maxRange=10) # min range could be 9 and maxrange could be 11, but set both to 10 and performance is a little better
                if locations is not None:
                    for loc in locations:
                        err = await self.do(tumor(BUILD_CREEPTUMOR_TUMOR, loc))
                        if not err:
                            tumorsMadeTumorPositions.add((tumor.position.x, tumor.position.y))
                            self.usedCreepTumors.add(tumor.tag)
                            break

    async def on_step(self, iteration):
        """""""""""""""
        PRIORITY:
        BUILD ORDER -> OVERLORDS -> EXPANDING -> EXTRACTORS -> CREEP SPREAD -> UPGRADES -> BUILDINGS -> UNIT MOVEMENT -> UNIT PRODUCTION (Drone -> Queen -> Army)
        """""""""""""""
        # on_step Intializations
        # Note: used frequently for building, upgrade, and production prioritizations
        self.enableArmyProduction = [True]
        self.enableDroneProduction = [True]
        self.enableQueenProduction = [True] # Only used when building Lair and Hive

        # Unit Count (existing and in production)
        self.actualOverlordCount =      self.units(OVERLORD).amount + self.already_pending(OVERLORD)
        self.actualQueenCount =         self.units(QUEEN).amount + self.already_pending(QUEEN)
        self.actualZerglingPairCount =  self.units(ZERGLING).amount + self.already_pending(ZERGLING)
        self.actualRoachCount =         self.units(ROACH).amount + self.already_pending(ROACH)
        self.actualHydraliskCount =     self.units(HYDRALISK).amount + self.already_pending(HYDRALISK)
        self.actualCorruptorCount =     self.units(CORRUPTOR).amount + self.already_pending(CORRUPTOR)
        self.actualBroodlordCount =     self.units(BROODLORD).amount + self.units(BROODLORDCOCOON).amount

        # Worker Supply (existing + in production + in gas)
        self.actualDroneSupply = self.units(DRONE).amount + self.already_pending(DRONE) + self.units(EXTRACTOR).ready.filter(lambda x:x.vespene_contents > 0).amount
        # Army Supply (Food supply of all units except Drones and Overlords)
        self.actualArmySupply = 2 * self.actualQueenCount + 1 * self.actualZerglingPairCount + 2 * self.actualRoachCount + 2 * self.actualHydraliskCount + 2 * self.actualCorruptorCount + 4 * self.actualBroodlordCount

        self.partneredQueenLimit = 4 # Maximum number of Partnered Queens

        ### Need to implement gas prioritization
        await self.distribute_workers()

        """""""""""""""
             BUILD
             ORDER
        """""""""""""""
        # Start Drone Immediately
        # Note: also accounts for sub 13 supply, in case of going under
        if self.actualDroneSupply < 13 and self.can_afford(DRONE) and self.supply_left >= 1 and self.units(LARVA).exists:
            await self.do(self.units(LARVA).random.train(DRONE))

        # Start Second Overlord on 13
        if self.actualDroneSupply == 13 and not self.already_pending(OVERLORD) and self.supply_used < 200 and self.units(LARVA).exists:
            self.enableDroneProduction.append(False)
            if self.can_afford(OVERLORD):
                await self.do(self.units(LARVA).random.train(OVERLORD))

        # Start Spawning Pool on 17
        # Note: Second Hatchery and Extractor must have already been started
        if self.actualDroneSupply == 17 and self.units(DRONE).exists and self.units(EXTRACTOR).amount >= 1 and self.townhalls.amount >= 2:
            if self.units(SPAWNINGPOOL).amount + self.already_pending(SPAWNINGPOOL) < 1:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(SPAWNINGPOOL):
                    await self.build(SPAWNINGPOOL, near = self.townhalls.first.position.towards(self.game_info.map_center, 5))

        # Partners a Queen to a Townhall
        # @parameter - Maximum number of Queens that will be dedicated to injecting
        self.partnerQueen(self.partneredQueenLimit)

        # Start Injecting
        # Note: Also reassigns Queens in case an Injecting Queen or Townhall dies
        await self.doQueenInjects(iteration)

        # Start Zerglings once Spawning Pool is finished
        if all(self.enableArmyProduction) and self.units(SPAWNINGPOOL).ready and self.actualZerglingPairCount < 2 and self.units(LARVA).exists and self.supply_left >= 1:
            self.enableDroneProduction.append(False)
            if self.can_afford(ZERGLING):
                await self.do(self.units(LARVA).random.train(ZERGLING))

        # Start Third Overlord on 20
        if self.actualDroneSupply == 20 and not self.already_pending(OVERLORD) and self.supply_used < 200 and self.units(LARVA).exists:
            self.enableDroneProduction.append(False)
            self.enableQueenProduction.append(False)
            if self.can_afford(OVERLORD):
                await self.do(self.units(LARVA).random.train(OVERLORD))
        """""""""""""""
            TOWNHALL
            UPGRADES
        """""""""""""""
        # Start Lair
        if self.units(HATCHERY).ready.idle.exists and self.townhalls.ready.amount >= 3 and self.actualDroneSupply > 50 and self.units(SPAWNINGPOOL).ready:
            if not self.lairStarted:
                self.enableArmyProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableQueenProduction.append(False)
                if self.can_afford(LAIR):
                    await self.do(self.units(HATCHERY).ready.idle.random(UPGRADETOLAIR_LAIR))
                    await self.chat_send(str(int(self.minutesElapsed())) + "min " + str(int(self.time - 60 * int(self.minutesElapsed()))) + "sec - Lair Starts")
                    self.lairStarted = True

        # Start Hive
        if self.units(LAIR).ready.idle.exists and self.townhalls.ready.amount >= 5 and self.actualDroneSupply > 80 and self.units(INFESTATIONPIT).ready.exists and self.units(SPIRE).exists:
            if not self.hiveStarted:
                self.enableArmyProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableQueenProduction.append(False)
                if self.can_afford(HIVE):
                    await self.do(self.units(LAIR).ready.idle.random(UPGRADETOHIVE_HIVE))
                    await self.chat_send(str(int(self.minutesElapsed())) + "min " + str(int((self.time - 60 * int(self.minutesElapsed())))) + "sec - Hive Starts")
                    self.hiveStarted = True
        """""""""""""""
             MACRO
           OVERLORDS
        """""""""""""""
        # Overlord Start Conditions (More than 3 Overlords)
        # At least 2 minutes have passed
        if self.units(LARVA).exists and self.supply_cap < 200 and self.supply_left <= 8 and self.minutesElapsed() > 2.0:
            if self.already_pending(OVERLORD) == 0:
                self.enableQueenProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(OVERLORD):
                    await self.do(self.units(LARVA).random.train(OVERLORD))
            elif self.supply_left <= 4 and self.already_pending(OVERLORD) == 1:
                self.enableQueenProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(OVERLORD):
                    await self.do(self.units(LARVA).random.train(OVERLORD))
        """""""""""""""
             MACRO
           EXPANDING
        """""""""""""""
        if self.minutesElapsed() >= 5 and self.actualDroneSupply >= 44 and self.townhalls.amount >= 3:       self.townhallsLimit = 8
        elif self.actualDroneSupply >= 29 and self.actualQueenCount >= 2 and self.townhalls.amount == 2:     self.townhallsLimit = 3
        elif self.actualDroneSupply >= 17:                                                                   self.townhallsLimit = 2
        else:                                                                                                self.townhallsLimit = 1

        if self.townhalls.amount < self.townhallsLimit and self.units(DRONE).exists:
            if not self.already_pending(HATCHERY):
                self.enableArmyProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableQueenProduction.append(False)
                if self.can_afford(HATCHERY):
                    await self.expand_now()
            elif self.already_pending(HATCHERY) == 1 and self.townhallsLimit >= 5 and self.minerals > 750:
                await self.expand_now()
        """""""""""""""
             MACRO
           EXTRACTOR
        """""""""""""""
        if self.townhalls.amount >= 4 and self.actualDroneSupply >= 66:            self.extractorLimit = self.townhalls.ready.amount * 2
        elif self.townhalls.amount >= 2 and self.units(ROACHWARREN).exists:        self.extractorLimit = 3
        elif self.townhalls.amount >= 2 and self.actualDroneSupply >= 17:          self.extractorLimit = 1
        else:                                                                      self.extractorLimit = 0

        for base in self.townhalls.ready:
            considered_vespene = self.state.vespene_geyser.closer_than(10.0, base)
            for target_vespene in considered_vespene:
                drone = self.select_build_worker(target_vespene.position)
                if drone is None or target_vespene is None:
                    break
                if self.units(EXTRACTOR).amount + self.already_pending(EXTRACTOR) < self.extractorLimit:
                    self.enableDroneProduction.append(False)
                    if self.can_afford(EXTRACTOR):
                        await self.do(drone.build(EXTRACTOR, target_vespene))
                        break
        """""""""""""""
             CREEP
           SPREADING
        """""""""""""""
        await self.spreadCreep()
        """""""""""""""
             MACRO
            UPGRADE
        """""""""""""""
        # Research Metabolic Boost and Adrenal Glands
        if self.units(SPAWNINGPOOL).ready:
            for spawning_pool in self.units(SPAWNINGPOOL).ready.noqueue:
                available_zergling_upgrades = await self.get_available_abilities(spawning_pool)
                important_zergling_upgrades = [AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST, AbilityId.RESEARCH_ZERGLINGADRENALGLANDS]
                for ability in important_zergling_upgrades:
                    if ability in available_zergling_upgrades:
                        self.enableDroneProduction.append(False)
                        self.enableArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(spawning_pool(ability))

        # Research Glial Regeneration (technically Reconstitution) and Tunneling Claws
        if self.units(ROACHWARREN).ready and self.units(LAIR).ready:
            for roach_warren in self.units(ROACHWARREN).ready.noqueue:
                available_roach_upgrades = await self.get_available_abilities(roach_warren)
                important_roach_upgrades = [AbilityId.RESEARCH_GLIALREGENERATION, AbilityId.RESEARCH_TUNNELINGCLAWS]
                for ability in important_roach_upgrades:
                    if ability in available_roach_upgrades:
                        self.enableDroneProduction.append(False)
                        self.enableArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(roach_warren(ability))

        # Research Muscular Augments and Grooved Spines
        if self.units(HYDRALISKDEN).ready:
            for hydralisk_den in self.units(HYDRALISKDEN).ready.noqueue:
                available_hydra_upgrades = await self.get_available_abilities(hydralisk_den)
                important_hydra_upgrades = [AbilityId.RESEARCH_MUSCULARAUGMENTS, AbilityId.RESEARCH_GROOVEDSPINES]
                for ability in important_hydra_upgrades:
                    if ability in available_hydra_upgrades:
                        self.enableDroneProduction.append(False)
                        self.enableArmyProduction.append(False)
                        if self.can_afford(ability):
                            await self.do(hydralisk_den(ability))

        # Research Missile and Armor Upgrades immediately after Evolution Chambers finished
        if self.units(EVOLUTIONCHAMBER).ready and not self.units(HIVE).ready:
            for evolution_chamber in self.units(EVOLUTIONCHAMBER).ready.noqueue:
                if not self.units(HIVE).ready:
                    available_evolution_upgrades = await self.get_available_abilities(evolution_chamber)
                    important_evolution_upgrades = [AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2, \
                    AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1, \
                    AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3]
                    for ability in important_evolution_upgrades:
                        if ability in available_evolution_upgrades:
                            self.enableDroneProduction.append(False)
                            self.enableArmyProduction.append(False)
                            if self.can_afford(ability):
                                await self.do(evolution_chamber(ability))
                else:
                    available_evolution_upgrades = await self.get_available_abilities(evolution_chamber)
                    important_evolution_upgrades = [AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2, \
                    AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1, \
                    AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3, \
                    AbilityID.RESEARCH_ZERGMELEEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3]
                    for ability in important_evolution_upgrades:
                        if ability in available_evolution_upgrades:
                            self.enableDroneProduction.append(False)
                            self.enableArmyProduction.append(False)
                            if self.can_afford(ability):
                                await self.do(evolution_chamber(ability))

        # Research Burrow once lair is finished
        if not self.burrowUpgradeStarted and self.units(LAIR).ready:
            for hatch in self.units(HATCHERY).ready.noqueue:
                abilities = await self.get_available_abilities(hatch)
                if AbilityId.RESEARCH_BURROW in abilities:
                    self.enableArmyProduction.append(False)
                    self.enableDroneProduction.append(False)
                    self.enableQueenProduction.append(False)
                    if self.can_afford(AbilityId.RESEARCH_BURROW):
                        await self.do(hatch(AbilityId.RESEARCH_BURROW))
                        self.burrowUpgradeStarted = True
        """""""""""""""
             MACRO
           BUILDINGS
        """""""""""""""
        # Roach Warren at 44 Drones
        # At least 44 drones and Spawning Pool is finished
        if self.units(DRONE).exists and self.actualDroneSupply >= 44 and self.units(SPAWNINGPOOL).ready and self.townhalls.exists:
            if self.units(ROACHWARREN).amount + self.already_pending(ROACHWARREN) < 1:
                self.enableArmyProduction.append(False)
                self.enableDroneProduction.append(False)
                if self.can_afford(ROACHWARREN):
                    await self.build(ROACHWARREN, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Evolution Chamber (x2) Start Conditions
        # At least 50 drones, roach warren exists, and at least 3 townhalls
        if self.units(DRONE).exists and self.actualDroneSupply >= 50 and self.townhalls.amount >= 3 and self.units(ROACHWARREN).exists:
            if self.units(EVOLUTIONCHAMBER).amount + self.already_pending(EVOLUTIONCHAMBER) < 2:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.minerals > 150:
                    await self.build(EVOLUTIONCHAMBER, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))
                    await self.build(EVOLUTIONCHAMBER, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Hydralisk Den immediatley after Lair finishes
        if self.units(DRONE).exists and self.units(LAIR).ready.exists:
            if self.units(HYDRALISKDEN).amount + self.already_pending(HYDRALISKDEN) < 1:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(HYDRALISKDEN):
                    await self.build(HYDRALISKDEN, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Infestation Pit: Lair is finished, at least 4 bases, and at least 7:00
        if self.units(DRONE).exists and self.units(LAIR).ready and self.minutesElapsed() > 7 and self.actualDroneSupply >= 55 and self.townhalls.amount >= 4:
            if self.units(INFESTATIONPIT).amount + self.already_pending(INFESTATIONPIT) < 1 and self.units(HYDRALISK).ready:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(INFESTATIONPIT):
                    await self.build(INFESTATIONPIT, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Spire: At least 160 supply off 4 townhalls, and at least 7:30
        if self.units(DRONE).exists and (self.units(LAIR).ready or self.units(HIVE).ready) and self.minutesElapsed() > 7.5 and self.supply_used >= 160 and self.townhalls.amount >= 5:
            if self.units(SPIRE).amount + self.already_pending(SPIRE) < 1:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(SPIRE):
                    await self.build(SPIRE, near = self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5))

        # Start Greater Spire immediately after hive is finished
        if self.units(HIVE).ready and self.units(SPIRE).ready.idle.exists:
            if not self.greaterspireStarted:
                self.enableArmyProduction.append(False)
                self.enableDroneProduction.append(False)
                self.enableQueenProduction.append(False)
                if self.can_afford(GREATERSPIRE):
                    await self.do(self.units(SPIRE).ready.idle.random(UPGRADETOGREATERSPIRE_GREATERSPIRE))
                    await self.chat_send(str(int(self.minutesElapsed())) + "min " + str(int((self.time - 60 * int(self.minutesElapsed())))) + "sec - Greater Spire Starts")
                    self.greaterspireStarted = True
        """""""""""""""
           TEMPORARY
         ATK ALGORITHM
        """""""""""""""
        # Attack if at least 190 Supply
        if self.supply_used >= 190:
            aggressive_units = {ROACH: [1], HYDRALISK: [1], OVERSEER: [1], BROODLORD: [1]}
            for attackforce in aggressive_units:
                for attacksquad in self.units(attackforce).idle:
                    for base in self.townhalls.ready:
                        if self.known_enemy_units.exists:
                            await self.do(attacksquad.attack(self.enemy_start_locations[0]))
            aggressive_lings = {ZERGLING: [6]}
            for lingforce in aggressive_lings:
                for lingsquad in self.units(lingforce).idle:
                    if self.known_enemy_units.exists:
                        await self.do(lingsquad.attack(random.choice(self.known_enemy_units)))
                    elif self.known_enemy_structures.exists:
                        await self.do(lingsquad.attack(random.choice(self.known_enemy_structures)))
        # Otherwise Defend
        else:
            defensive_units = {ZERGLING: [1], ROACH: [1], HYDRALISK: [1], OVERSEER: [1], BROODLORD: [1]}
            for defenseforce in defensive_units:
                for defensesquad in self.units(defenseforce).idle:
                    for base in self.townhalls:
                        # Defense Radius is 40
                        if self.known_enemy_units.closer_than(40.0, base).exists:
                            await self.do(defensesquad.attack(random.choice(self.known_enemy_units.closer_than(40.0, base))))
                        else:
                            await self.do(defensesquad.move(self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5)))
            defensive_queens = {QUEEN: [1]}
            for defensequeen in defensive_queens:
                for queensquad in self.units(defensequeen).idle:
                    for base in self.townhalls:
                        if self.known_enemy_units.closer_than(40.0, base).exists:
                            await self.do(queensquad.attack(random.choice(self.known_enemy_units.closer_than(40.0, base))))
                        else:
                            await self.do(queensquad.attack(self.units(HATCHERY).first.position.towards(self.game_info.map_center, 5)))
        """""""""""""""
        UNIT PRODUCTION AT END OF ITERATION
        FOR UPGRADE/BUILDING PRIORITIZATION
        """""""""""""""

        """""""""""""""
             MACRO
            DRONING
        """""""""""""""
        if self.townhalls.ready.amount >= 4: self.droneLimit = 85
        else:                                self.droneLimit = 66

        if all(self.enableDroneProduction) and self.actualDroneSupply < self.droneLimit and self.supply_left >= 1 and self.units(LARVA).exists and self.actualDroneSupply < 22 * self.townhalls.ready.amount:
            if self.can_afford(DRONE):
                if self.actualDroneSupply < 1.5 * self.actualArmySupply or not self.units(ROACHWARREN).ready:
                    await self.do(self.units(LARVA).random.train(DRONE))
        """""""""""""""
             MACRO
        QUEEN PRODUCTION
        """""""""""""""
        # Queens cap at 12 since only 8 townhalls are allowed
        if self.townhalls.ready.amount >= 3 and self.units(SPAWNINGPOOL).ready \
        and self.units(LAIR).exists:                                                  self.queenLimit = self.townhalls.ready.amount + 4
        elif self.townhalls.ready.amount == 2 and self.units(SPAWNINGPOOL).ready:     self.queenLimit = 3
        else:                                                                         self.queenLimit = 0

        # Early Game Queen Production Conditions
        # Spawning Pool exists and fewer than 2 or fewer townhalls are ready
        if all(self.enableQueenProduction) and self.supply_left >= 2 and self.actualQueenCount < self.queenLimit:
            for hatch in self.units(HATCHERY).ready.noqueue:
                self.enableDroneProduction.append(False)
                self.enableArmyProduction.append(False)
                if self.can_afford(QUEEN):
                    await self.do(hatch.train(QUEEN))

        """""""""""""""
             MACRO
           ARMY UNIT
        """""""""""""""
        self.enableZerglingProduction = False
        self.enableRoachProduction = False
        self.enableHydraliskProduction = False
        self.enableCorrupterProduction = False
        self.enableBroodlordProduction = False

        if self.units(SPAWNINGPOOL).ready:
            if self.townhalls.ready.amount >= 3 and self.actualZerglingPairCount < 10 \
            and not self.units(GREATERSPIRE).ready.exists and self.supply_used < 90:                         self.enableZerglingProduction = True
            elif self.townhalls.ready.amount >= 3 and self.actualZerglingPairCount < 10 \
            and self.units(GREATERSPIRE).ready.exists \
            and self.supply_used < 60 + self.actualCorruptorCount + self.actualBroodlordCount:               self.enableZerglingProduction = True

        if self.units(ROACHWARREN).ready:
            if not self.units(HYDRALISKDEN).ready and not self.units(GREATERSPIRE).ready:                    self.enableRoachProduction = True
            elif self.units(HYDRALISKDEN).ready and not self.units(GREATERSPIRE).ready \
            and self.actualRoachCount < 0.50 * self.actualHydraliskCount and self.supply_used < 190:         self.enableRoachProduction = True

        if self.units(HYDRALISKDEN).ready:
            if not self.units(GREATERSPIRE).ready:                                                           self.enableHydraliskProduction = True
            elif self.units(GREATERSPIRE).ready \
            and self.supply_used < 160 + self.actualCorruptorCount + self.actualBroodlordCount:              self.enableHydraliskProduction = True

        if self.units(GREATERSPIRE).ready:
            if self.actualCorruptorCount + self.actualBroodlordCount < 7:                                    self.enableCorrupterProduction = True
            if self.units(CORRUPTOR).idle.exists:                                                            self.enableBroodlordProduction = True

        # BUILD UNITS
        if all(self.enableArmyProduction) and self.units(LARVA).exists:

            # Start Zerglings once Spawning Pool is finished
            if self.enableZerglingProduction and self.supply_left >= 1:
                if self.can_afford(ZERGLING):
                    await self.do(self.units(LARVA).random.train(ZERGLING))

            # Start Roaches once Roach Warren is finished
            if self.enableRoachProduction and self.supply_left >= 2:
                    if self.can_afford(ROACH):
                        await self.do(self.units(LARVA).random.train(ROACH))

            # Start Hydralisks once Hydralisk Den is finished
            if self.enableHydraliskProduction and self.supply_left >= 2:
                if self.can_afford(HYDRALISK):
                        await self.do(self.units(LARVA).random.train(HYDRALISK))

        # Corrupters/Broodlords are not limited by enableArmyProduction
        # Start Corrupters once Greater Spire is finished
        if self.enableCorrupterProduction and self.supply_left >= 2:
            if self.can_afford(CORRUPTOR):
                await self.do(self.units(LARVA).random.train(CORRUPTOR))

        # Morph Broodlord once Corrupter is finished
        if self.enableBroodlordProduction and self.supply_left >= 2:
            if self.can_afford(BROODLORD):
                LowestHealthIdleCorrupter = min(self.units(CORRUPTOR), key=lambda x:x.health)
                await self.do(LowestHealthIdleCorrupter(MORPHTOBROODLORD_BROODLORD))
"""""""""""""""
    TESTING
"""""""""""""""
def main():
    """""""""""""""
    [0] Terran | [1] Protoss | [2] Zerg | [3] Random
    [0] Easy | [1] Medium | [2] Hard | [3] Elite | [4] Cheat Vision | [5] Cheat Money | [6] Cheat Insane
    """""""""""""""
    COMPUTER_RACE = [Race.Terran, Race.Protoss, Race.Zerg, Race.Random]
    COMPUTER_DIFFICULTY = [Difficulty.Easy, Difficulty.Medium, Difficulty.Hard, Difficulty.VeryHard, Difficulty.CheatVision, Difficulty.CheatMoney, Difficulty.CheatInsane]

    sc2.run_game(maps.get("CyberForestLE"), [
        Bot(Race.Zerg, AreologyBot()),
        Computer(COMPUTER_RACE[3], COMPUTER_DIFFICULTY[3])
    ], realtime = False, save_replay_as="AreologyBot.SC2Replay")

if __name__ == '__main__':
    main()
