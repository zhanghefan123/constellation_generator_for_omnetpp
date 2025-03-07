from generator.ospf import ScriptGeneratorOspf
from generator.lipsin import ScriptGeneratorLipsin
from generator.none import ScriptGeneratorNone
from generator.sr import ScriptGeneratorSR
from loguru import logger
from modules import ModuleTypes as mtm


class ScriptGeneratorFactory:
    def __init__(self, project):
        self.protocol = project.constellation.config_reader.routing_protocol
        self.config_reader = project.constellation.config_reader
        self.project = project
        self.logger = logger

    def create_generator(self):
        if self.protocol == mtm.RoutingProtocols.NONE:
            final_generator = ScriptGeneratorNone.ScriptGeneratorNone(self.project)
        elif self.protocol == mtm.RoutingProtocols.IP_OSPF:
            final_generator = ScriptGeneratorOspf.ScriptGeneratorOspf(self.project)
        elif self.protocol == mtm.RoutingProtocols.LIPSIN:
            final_generator = ScriptGeneratorLipsin.ScriptGeneratorLipsin(self.project)
        elif self.protocol == mtm.RoutingProtocols.SR:
            final_generator = ScriptGeneratorSR.ScriptGeneratorSR(self.project)
        else:
            logger.error("Unknown routing protocol: " + str(self.protocol))
            raise ValueError("Unknown routing protocol: " + str(self.protocol))
        return final_generator
