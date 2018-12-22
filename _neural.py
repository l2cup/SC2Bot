import sc2
from sc2.constants import *
import cv2
import numpy as np


class Neural(sc2.BotAI):

    async def draw(self):
        await self.draw_friendly()
        await self.draw_enemy()
        self.flipped = cv2.flip(self.game_data, 0)
        resized = cv2.resize(self.flipped, dsize=None, fx=2, fy=2)
        cv2.imshow('Model', resized)
        cv2.waitKey(1)

    async def draw_friendly(self):
        self.game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
        draw_dict = {
                     NEXUS: [15, (0, 255, 0)],
                     PYLON: [3, (20, 235, 0)],
                     PROBE: [1, (55, 200, 0)],
                     ASSIMILATOR: [2, (55, 200, 0)],
                     GATEWAY: [3, (200, 100, 0)],
                     CYBERNETICSCORE: [3, (150, 150, 0)],
                     STARGATE: [5, (255, 0, 0)],
                     ROBOTICSFACILITY: [5, (215, 155, 0)],
                     VOIDRAY: [3, (255,100,0)],
                     OBSERVER: [1, (255,255,255)]
                    }

        for unit_type in draw_dict:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(self.game_data, (int(pos[0]), int(pos[1])), draw_dict[unit_type][0], draw_dict[unit_type][1], -1)

    
    async def draw_enemy(self):
        main_base_names = ["NEXUS", "COMMANDCENTER", "HATCHERY", "ORBITALCOMMAND", "LAIR", "PLANETARYFORTRESS", "HIVE"]
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name not in main_base_names:
                cv2.circle(self.game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
            else:
                cv2.circle(self.game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)

        for enemy_unit in self.known_enemy_units:

            if not enemy_unit.is_structure:
                worker_names = ["PROBE",
                                "SCV",
                                "DRONE"]

                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(self.game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(self.game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)
