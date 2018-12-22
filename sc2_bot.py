from _macro import Macro
from _units import Units
from _micro import Micro
from _neural import Neural
import keras

class SCIIBot(Macro, Units, Micro,Neural):

    def __init__(self):
        self.scouts_and_spots = {}
        self.ITERATIONS_PER_MINUTE = 165
        self.do_something_after = 0
        self.model = keras.models.load_model("BasicCNN-30-epochs-0.0001-LR-4.2")
    
    async def on_step(self, iteration):
        self.iteration = iteration
        await Macro.manage_macro(self, iteration)
        await Units.manage_units(self)
        await Micro.manage_micro(self)
        await Neural.draw(self)
