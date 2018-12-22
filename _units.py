import sc2
from sc2.constants import *
import math


class Units(sc2.BotAI):

    async def manage_units(self):
        await self.train_units()
        await self.build_scout()

    async def train_units(self):
        for sg in self.units(UnitTypeId.STARGATE).ready.noqueue:
            if self.can_afford(UnitTypeId.VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(UnitTypeId.VOIDRAY))

    async def build_scout(self):
        if len(self.units(OBSERVER)) < math.floor(self.time/3) and len(self.units(OBSERVER)) < 4:
            for rf in self.units(ROBOTICSFACILITY).ready.noqueue:
                print(len(self.units(OBSERVER)), self.time/3)
                if self.can_afford(OBSERVER) and self.supply_left > 0:
                    await self.do(rf.train(OBSERVER))
