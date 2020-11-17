from common import ScModule, ScAgent, ScEventParams
from sc import *


class MicroClimateChartAgent(ScAgent):
    def RunImpl(self, evt: ScEventParams) -> ScResult:
        return ScResult.Ok
