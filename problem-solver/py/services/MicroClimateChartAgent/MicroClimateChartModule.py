from common import ScModule, ScKeynodes, ScPythonEventType
from keynodes import Keynodes
from MicroClimateChartAgent import MicroClimateChartAgent

from sc import *


class MicroClimateChartModule(ScModule):

    def __init__(self):
        ScModule.__init__(
            self,
            ctx=__ctx__,
            cpp_bridge=__cpp_bridge__,
            keynodes=[
                'microclimate_record',
                'temperature',
                'humidity',
                'nrel_celsius_mesurement',
                'nrel_value',
                'nrel_percental_mesurement'
            ],
        )

    def OnInitialize(self, params):
        print('Initialize MicroClimateChart module')
        mcShuttedDown = self.ctx.HelperResolveSystemIdtf("mcShuttedDown", ScType.NodeConst)

        agent = MicroClimateChartAgent(self)
        agent.Register(mcShuttedDown, ScPythonEventType.EraseElement)

        self.ctx.DeleteElement(mcShuttedDown)

    def OnShutdown(self):
        print('Shutting down MicroClimateChart module')


service = MicroClimateChartModule()
service.Run()
