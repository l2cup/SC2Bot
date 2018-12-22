import sc2
from sc2.constants import *


class Macro(sc2.BotAI):

    async def manage_macro(self, iteration):
        await self.distribute_workers()
        await self.build_probes()
        await self.build_pylons()
        await self.chrono_boost()
        await self.manage_idle_probes()
        await self.build_offensive(iteration)
        await self.research_air()
        await self.build_asimilator()
        await self.expand()

    async def build_probes(self):
        if self.workers.amount < self.units(UnitTypeId.NEXUS).amount*22:
            for nexus in self.units(UnitTypeId.NEXUS).ready.noqueue:
                if self.can_afford(UnitTypeId.PROBE):
                    await self.do(nexus.train(UnitTypeId.PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and self.townhalls.exists and self.supply_used >= 14 and self.can_afford(UnitTypeId.PYLON) and \
           self.units(UnitTypeId.PYLON).not_ready.amount + self.already_pending(UnitTypeId.PYLON) < 1:
            ws = self.workers.gathering
            if ws:
                w = ws.furthest_to(ws.center)
                loc = await self.find_placement(UnitTypeId.PYLON, self.units(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center, 8), placement_step=5)
                if loc:
                    await self.do(w.build(UnitTypeId.PYLON, loc))

    async def build_asimilator(self):
        for nexus in self.units(UnitTypeId.NEXUS):
            geysers = self.state.vespene_geyser.closer_than(10, nexus)
            for vg in geysers:
                if await self.can_place(UnitTypeId.ASSIMILATOR, vg.position) and self.can_afford(UnitTypeId.ASSIMILATOR) and vg.has_vespene:
                    ws = self.workers.gathering
                    if ws.exists:
                        w = ws.closest_to(vg)
                        await self.do(w.build(UnitTypeId.ASSIMILATOR, vg))

    async def build_offensive(self, iteration):
        if self.units(UnitTypeId.PYLON).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random

            if not self.units(UnitTypeId.GATEWAY).ready.exists and \
               self.units(UnitTypeId.GATEWAY).not_ready.amount + self.already_pending(UnitTypeId.GATEWAY) < 1:
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=pylon, placement_step=3)
            elif self.units(UnitTypeId.GATEWAY).ready.exists and not self.units(UnitTypeId.CYBERNETICSCORE).ready.exists and \
                    self.units(UnitTypeId.CYBERNETICSCORE).not_ready.amount + self.already_pending(UnitTypeId.CYBERNETICSCORE) < 1:
                await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon, placement_step=6)

            if self.units(CYBERNETICSCORE).ready.exists and self.units(UnitTypeId.STARGATE).ready.amount > 1:
                if len(self.units(ROBOTICSFACILITY)) < 1:
                    if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                        await self.build(ROBOTICSFACILITY, near=pylon)

            if self.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
                if len(self.units(UnitTypeId.STARGATE)) < ((iteration / self.ITERATIONS_PER_MINUTE) / 2) and \
                   self.can_afford(UnitTypeId.STARGATE) and \
                   self.already_pending(UnitTypeId.STARGATE) + self.units(UnitTypeId.STARGATE).not_ready.amount < 1:
                    await self.build(UnitTypeId.STARGATE, near=pylon, placement_step=3)

    async def research_air(self):
        if self.units(UnitTypeId.CYBERNETICSCORE).ready.noqueue.exists:
            c = self.units(UnitTypeId.CYBERNETICSCORE).ready.noqueue.first
            if self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL1) == 0:
                await self.do(c(RESEARCH_PROTOSSAIRWEAPONS))
            if self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL1) == 0:
                await self.do(c(RESEARCH_PROTOSSAIRARMOR))

    async def expand(self):
        if self.can_afford(UnitTypeId.NEXUS) and self.already_pending(UnitTypeId.NEXUS) == 0 and 1 <= self.townhalls.amount < 2 and \
           len(self.units(UnitTypeId.STARGATE).ready) > 2:
            next_expo = await self.get_next_expansion()
            location = await self.find_placement(UnitTypeId.NEXUS, next_expo, placement_step=1)
            if location:
                w = self.select_build_worker(location)
                if w and self.can_afford(UnitTypeId.NEXUS):
                    error = await self.do(w.build(UnitTypeId.NEXUS, location))
                    if error:
                        print(error)

    async def chrono_boost(self):
        for nexus in self.units(UnitTypeId.NEXUS).filter(lambda x: x.energy >= 50):
            if self.units(UnitTypeId.STARGATE).ready:
                for sg in self.units(UnitTypeId.STARGATE).ready:
                    if not sg.is_idle and not sg.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        await self.do(
                            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, target=sg))
                        break

            elif not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, target=nexus))

    ##################################################################################################################
    ##################################################################################################################
    # HELPER METHODS

    # Helper method, already_pending rewritten to include buildings aswell

    def already_pending(self, unit_type):
        ability = self._game_data.units[unit_type.value].creation_ability
        unitAttributes = self._game_data.units[unit_type.value].attributes

        buildings_in_construction = self.units.structure(unit_type).not_ready
        if 8 not in unitAttributes and any(o.ability == ability for w in (self.units.not_structure) for o in w.orders):
            return sum([o.ability == ability for w in (self.units - self.workers) for o in w.orders])
        # following checks for unit production in a building queue, like queen, also checks if hatch is morphing to LAIR
        elif any(o.ability.id == ability.id for w in (self.units.structure) for o in w.orders):
            return sum([o.ability.id == ability.id for w in (self.units.structure) for o in w.orders])
        # the following checks if a worker is about to start a construction (and for scvs still constructing if not checked for structures with same position as target)
        elif any(o.ability == ability for w in self.workers for o in w.orders):
            return sum([o.ability == ability for w in self.workers for o in w.orders]) \
                - buildings_in_construction.amount
        elif any(egg.orders[0].ability == ability for egg in self.units(UnitTypeId.EGG)):
            return sum([egg.orders[0].ability == ability for egg in self.units(UnitTypeId.EGG)])
        return 0

    async def distribute_workers(self, performanceHeavy=True, onlySaturateGas=False):
        # expansion_locations = self.expansion_locations
        # owned_expansions = self.owned_expansions

        mineralTags = [x.tag for x in self.state.units.mineral_field]
        # gasTags = [x.tag for x in self.state.units.vespene_geyser]
        geyserTags = [x.tag for x in self.geysers]

        workerPool = self.units & []
        workerPoolTags = set()

        # find all geysers that have surplus or deficit
        deficitGeysers = {}
        surplusGeysers = {}
        for g in self.geysers.filter(lambda x: x.vespene_contents > 0):
            # only loop over geysers that have still gas in them
            deficit = g.ideal_harvesters - g.assigned_harvesters
            if deficit > 0:
                deficitGeysers[g.tag] = {"unit": g, "deficit": deficit}
            elif deficit < 0:
                surplusWorkers = self.workers.closer_than(10, g).filter(lambda w: w not in workerPoolTags and len(
                    w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in geyserTags)
                # workerPool.extend(surplusWorkers)
                for i in range(-deficit):
                    if surplusWorkers.amount > 0:
                        w = surplusWorkers.pop()
                        workerPool.append(w)
                        workerPoolTags.add(w.tag)
                surplusGeysers[g.tag] = {"unit": g, "deficit": deficit}

        # find all townhalls that have surplus or deficit
        deficitTownhalls = {}
        surplusTownhalls = {}
        if not onlySaturateGas:
            for th in self.townhalls:
                deficit = th.ideal_harvesters - th.assigned_harvesters
                if deficit > 0:
                    deficitTownhalls[th.tag] = {"unit": th, "deficit": deficit}
                elif deficit < 0:
                    surplusWorkers = self.workers.closer_than(10, th).filter(lambda w: w.tag not in workerPoolTags and len(
                        w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                    # workerPool.extend(surplusWorkers)
                    for i in range(-deficit):
                        if surplusWorkers.amount > 0:
                            w = surplusWorkers.pop()
                            workerPool.append(w)
                            workerPoolTags.add(w.tag)
                    surplusTownhalls[th.tag] = {"unit": th, "deficit": deficit}

            if all([len(deficitGeysers) == 0, len(surplusGeysers) == 0, len(surplusTownhalls) == 0 or deficitTownhalls == 0]):
                # cancel early if there is nothing to balance
                return

        # check if deficit in gas less or equal than what we have in surplus, else grab some more workers from surplus bases
        deficitGasCount = sum(
            gasInfo["deficit"] for gasTag, gasInfo in deficitGeysers.items() if gasInfo["deficit"] > 0)
        surplusCount = sum(-gasInfo["deficit"] for gasTag,
                           gasInfo in surplusGeysers.items() if gasInfo["deficit"] < 0)
        surplusCount += sum(-thInfo["deficit"] for thTag,
                            thInfo in surplusTownhalls.items() if thInfo["deficit"] < 0)

        if deficitGasCount - surplusCount > 0:
            # grab workers near the gas who are mining minerals
            for gTag, gInfo in deficitGeysers.items():
                if workerPool.amount >= deficitGasCount:
                    break
                workersNearGas = self.workers.closer_than(10, gInfo["unit"]).filter(lambda w: w.tag not in workerPoolTags and len(
                    w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                while workersNearGas.amount > 0 and workerPool.amount < deficitGasCount:
                    w = workersNearGas.pop()
                    workerPool.append(w)
                    workerPoolTags.add(w.tag)

        # now we should have enough workers in the pool to saturate all gases, and if there are workers left over, make them mine at townhalls that have mineral workers deficit
        for gTag, gInfo in deficitGeysers.items():
            if performanceHeavy:
                # sort furthest away to closest (as the pop() function will take the last element)
                workerPool.sort(key=lambda x: x.distance_to(
                    gInfo["unit"]), reverse=True)
            for i in range(gInfo["deficit"]):
                if workerPool.amount > 0:
                    w = workerPool.pop()
                    if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                        await self.do(w.gather(gInfo["unit"], queue=True))
                    else:
                        await self.do(w.gather(gInfo["unit"]))

        if not onlySaturateGas:
            # if we now have left over workers, make them mine at bases with deficit in mineral workers
            for thTag, thInfo in deficitTownhalls.items():
                if performanceHeavy:
                    # sort furthest away to closest (as the pop() function will take the last element)
                    workerPool.sort(key=lambda x: x.distance_to(
                        thInfo["unit"]), reverse=True)
                for i in range(thInfo["deficit"]):
                    if workerPool.amount > 0:
                        w = workerPool.pop()
                        mf = self.state.mineral_field.closer_than(
                            10, thInfo["unit"]).closest_to(w)
                        if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                            await self.do(w.gather(mf, queue=True))
                        else:
                            await self.do(w.gather(mf))

    async def manage_idle_probes(self):
        if self.townhalls.exists:
            for w in self.workers.idle:
                th = self.townhalls.closest_to(w)
                mfs = self.state.mineral_field.closer_than(10, th)
                if mfs:
                    mf = mfs.closest_to(w)
                    await self.do(w.gather(mf))
