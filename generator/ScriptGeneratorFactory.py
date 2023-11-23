from modules import Constellation
from generator.ospf import ScriptGeneratorOspf
from generator.lipsin import ScriptGeneratorLipsin
from generator.none import ScriptGeneratorNone
from loguru import logger


class ScriptGeneratorFactory:
    def __init__(self, project):
        self.protocol = project.constellation.routingProtocol
        self.project = project
        self.logger = logger

    def create_generator(self):
        if self.protocol == Constellation.Constellation.RoutingProtocols.NONE:
            final_generator = ScriptGeneratorNone.ScriptGeneratorNone(self.project)
        elif self.protocol == Constellation.Constellation.RoutingProtocols.IP_OSPF:
            final_generator = ScriptGeneratorOspf.ScriptGeneratorOspf(self.project)
        elif self.protocol == Constellation.Constellation.RoutingProtocols.LIPSIN:
            final_generator = ScriptGeneratorLipsin.ScriptGeneratorLipsin(self.project)
        else:
            logger.error("Unknown routing protocol: " + str(self.protocol))
            raise ValueError("Unknown routing protocol: " + str(self.protocol))
        return final_generator
