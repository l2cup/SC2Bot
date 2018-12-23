import sc2
from sc2.constants import *
import random
import keras
import numpy as np
from sc2.unit import Unit
from sc2.position import Point2, Point3


class Micro(sc2.BotAI):

    async def manage_micro(self):
        await self.command_forces()
        await self.scout()

    async def command_forces(self):
        self.choice = -1
        if len(self.units(VOIDRAY).idle) > 0:

            target = False
            if self.iteration > self.do_something_after:
                prediction = self.model.predict(
                    [self.flipped.reshape([-1, 176, 200, 3])])
                self.choice = np.argmax(prediction[0])

                choice_dict = {0: "Wait and don't attack.",
                               1: "Defend Nexus.",
                               2: "Attack enemy structure.",
                               3: "Attack enemy starting position."}

                print("Choice #{}:{}".format(
                    self.choice, choice_dict[self.choice]))

                if self.choice == 0:
                    wait = random.randrange(20, 165)
                    self.do_something_after = self.iteration + wait

                elif self.choice == 1:
                    if len(self.known_enemy_units) > 0:
                        target = self.known_enemy_units.closest_to(
                            random.choice(self.units(NEXUS)))

                elif self.choice == 2:
                    if len(self.known_enemy_structures) > 0:
                        target = random.choice(self.known_enemy_structures)

                elif self.choice == 3:
                    target = self.enemy_start_locations[0]

                if target:
                    for vr in self.units(VOIDRAY).idle:
                        await self.do(vr.attack(target))

        for vr in self.units(VOIDRAY):
            if not vr.is_idle:
                enemyThreatsClose = self.known_enemy_units.filter(
                    lambda x: x.can_attack_air).closer_than(15, vr)
                enemyThreatsVeryClose = self.known_enemy_units.filter(
                    lambda x: x.can_attack_air).closer_than(4.5, vr)
                enemyUnits = self.known_enemy_units.closer_than(
                    7, vr)
                enemyCanAttackMeUnits = self.known_enemy_units.filter(
                    lambda x: x.can_attack_air).closer_than(7, vr)
                if vr.weapon_cooldown == 0 and enemyCanAttackMeUnits.exists:
                    print("MICRO 0")
                    enemyUnit = enemyCanAttackMeUnits.sorted(lambda x: x.distance_to(vr))[0]
                    await self.do(vr.attack(enemyUnit))
                    await self.ability_cast(vr, enemyUnit)
                    continue
                elif vr.weapon_cooldown == 0 and enemyUnits.exists:
                    print("MICRO 1")
                    enemyUnits = enemyUnits.sorted(
                        lambda x: x.distance_to(vr))
                    enemy = enemyUnits[0]
                    await self.do(vr.attack(enemy))
                    await self.ability_cast(vr, enemy)
                    continue
                elif enemyThreatsVeryClose.exists:
                    print("MICRO 2")
                    retreatPoints = self.neighbors8(
                        vr.position, distance=2) | self.neighbors8(vr.position, distance=4)
                    if retreatPoints:
                        closestEnemy = enemyThreatsVeryClose.closest_to(
                            vr)
                        retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(
                            closestEnemy) - x.distance_to(vr))
                        await self.do(vr.move(retreatPoint))
                        continue
                elif enemyThreatsClose.exists and vr.health_percentage < 2/5:
                    print("MICRO 3")
                    retreatPoints = self.neighbors8(
                        vr.position, distance=2) | self.neighbors8(vr.position, distance=4)
                    if retreatPoints:
                        closestEnemy = enemyThreatsClose.closest_to(
                            vr)
                        retreatPoint = closestEnemy.position.furthest(
                            retreatPoints)
                        await self.do(vr.move(retreatPoint))
                        continue
                else:
                    if self.known_enemy_units.filter(lambda x: x.can_attack_air).exists:
                        print("MICRO 4 AIR")
                        closestEnemy = self.known_enemy_units.filter(
                            lambda x: x.can_attack_air).closest_to(vr)
                        await self.do(vr.attack(closestEnemy))
                        continue

                    elif self.known_enemy_units.exists:
                        print("MICRO 4")
                        closestEnemy = self.known_enemy_units.closest_to(
                            vr)
                        await self.do(vr.attack(closestEnemy))
                        continue
                    else:
                        print("MICRO 5")
                        await self.do(vr.attack(self.random_location_variance(random.choice(self.enemy_start_locations))))
                        continue

    # def find_target(self, state):
    #     if len(self.known_enemy_units) > 0:
    #         return random.choice(self.known_enemy_units)
    #     elif len(self.known_enemy_structures) > 0:
    #         return random.choice(self.known_enemy_structures)
    #     else:
    #         return self.enemy_start_locations[0]

    async def ability_cast(self, vr, target):
        if target.is_armored:
            await self.do(vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))

    async def scout(self):

        # {DISTANCE_TO_ENEMY_START:EXPANSIONLOC}
        self.expand_dis_dir = {}

        for el in self.expansion_locations:
            distance_to_enemy_start = el.distance_to(
                self.enemy_start_locations[0])
            # print(distance_to_enemy_start)
            self.expand_dis_dir[distance_to_enemy_start] = el

        self.ordered_exp_distances = sorted(k for k in self.expand_dis_dir)

        existing_ids = [unit.tag for unit in self.units]
        # removing of scouts that are actually dead now.
        to_be_removed = []
        for noted_scout in self.scouts_and_spots:
            if noted_scout not in existing_ids:
                to_be_removed.append(noted_scout)

        for scout in to_be_removed:
            del self.scouts_and_spots[scout]
        # end removing of scouts that are dead now.

        if len(self.units(ROBOTICSFACILITY).ready) == 0:
            unit_type = PROBE
            unit_limit = 1
        else:
            unit_type = OBSERVER
            unit_limit = 15

        assign_scout = True

        if unit_type == PROBE:
            for unit in self.units(PROBE):
                if unit.tag in self.scouts_and_spots:
                    assign_scout = False

        if assign_scout:
            if len(self.units(unit_type).idle) > 0:
                for obs in self.units(unit_type).idle[:unit_limit]:
                    if obs.tag not in self.scouts_and_spots:
                        for dist in self.ordered_exp_distances:
                            try:
                                location = next(
                                    value for key, value in self.expand_dis_dir.items() if key == dist)
                                # DICT {UNIT_ID:LOCATION}
                                active_locations = [
                                    self.scouts_and_spots[k] for k in self.scouts_and_spots]

                                if location not in active_locations:
                                    if unit_type == PROBE:
                                        for unit in self.units(PROBE):
                                            if unit.tag in self.scouts_and_spots:
                                                continue

                                    await self.do(obs.move(location))
                                    self.scouts_and_spots[obs.tag] = location
                                    break
                            except Exception as e:
                                pass

        for obs in self.units(unit_type):
            if obs.tag in self.scouts_and_spots:
                if obs in [probe for probe in self.units(PROBE)]:
                    await self.do(obs.move(self.random_location_variance(self.scouts_and_spots[obs.tag])))

    def random_location_variance(self, location):
        x = location[0]
        y = location[1]

        #  FIXED THIS
        x += random.randrange(-5, 5)
        y += random.randrange(-5, 5)

        if x < 0:
            print("x below")
            x = 0
        if y < 0:
            print("y below")
            y = 0
        if x > self.game_info.map_size[0]:
            print("x above")
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            print("y above")
            y = self.game_info.map_size[1]

        go_to = sc2.position.Point2(sc2.position.Pointlike((x, y)))

        return go_to

    # stolen and modified from position.py
    def neighbors4(self, position, distance=1):
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),
            Point2((p.x + d, p.y)),
            Point2((p.x, p.y - d)),
            Point2((p.x, p.y + d)),
        }

    # stolen and modified from position.py
    def neighbors8(self, position, distance=1):
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }
