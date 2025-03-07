from generator import ScriptGeneratorBase
from typing import Tuple
from global_vars import GlobalVars
from modules import LipsinLink


class ScriptGeneratorSR(ScriptGeneratorBase.ScriptGeneratorBase):
    def __init__(self, project):
        super().__init__(project)

    def generateNedFile(self) -> Tuple[str, str]:
        """
        generate ned file
        :return:
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/OsgEarthNet.ned"
        final_str = f"package projects.{self.project.projectName};\n"
        with open("resources/sr/ned_pre_file") as reader:
            final_str += reader.read()
        final_str += self.generateChannelControllerNed()
        final_str += self.generate_global_module()
        # ----------------------  add satellite modules ----------------------
        for satellite in self.project.constellation.satellites:
            final_str += f"\t\tSAT{satellite.satellite_id}: {GlobalVars.SR_SATELLITE_MODULE_NAME}" + "{\n\r"
            final_str += f"\t\t\tparameters:\n\r"
            append_x = 0
            if satellite.index_in_orbit == 0 or (
                    satellite.index_in_orbit == self.project.constellation.config_reader.sat_per_orbit - 1):
                append_x = 50
            final_str += f'''\t\t\t\t@display("p={100 + 150 * satellite.orbit_id + append_x},{100 + 100 * satellite.index_in_orbit}");\n\r'''
            final_str += f"\t\t\tgates:\n\r"
            final_str += f"\t\t\t\tethg[{satellite.interfaceIndex + self.project.constellation.config_reader.satellite_gsl_interface_number}];\n\r"
            final_str += f"\t\t" + "}" + "\n\r"
        # ----------------------  add satellite modules ----------------------
        # ----------------------      add connections   ----------------------
        final_str += "\t connections allowunconnected:\n\r"
        for interSatelliteLink in self.project.constellation.ISLs:
            final_str += (f"\t\tSAT{interSatelliteLink.sourceSatellite.satellite_id}"
                          f".ethg[{interSatelliteLink.sourceInterfaceIndex}]"
                          f" <--> "
                          f"{self.project.constellation.config_reader.isl_link_bandwidth}"
                          f" <--> "
                          f"SAT{interSatelliteLink.destinationSatellite.satellite_id}"
                          f".ethg[{interSatelliteLink.destInterfaceIndex}];\n\r")
        final_str += "}"
        # ----------------------      add connections   ----------------------
        return writeFilePath, final_str

    def generateIniFile(self):
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/Starter.ini"
        final_str = "[General]\n"
        final_str += "network = OsgEarthNet\n"
        # preload file
        with open("resources/sr/ini_pre_file") as f:
            final_str += f.read()
        final_str += self.generateSimTimeIni()  # generate simtime
        final_str += self.checkPolarAreaEntering()  # generate whether to check polar entering
        # ----------------------      generate positions   ----------------------
        for satellite in self.project.constellation.satellites:
            final_str += f"""*.SAT{satellite.satellite_id}.mobility.orbitNormal = \"{satellite.orbitNorms[0]}, {satellite.orbitNorms[1]}, {satellite.orbitNorms[2]}\"\n"""
            final_str += f"*.SAT{satellite.satellite_id}.mobility.startingPhase = {satellite.startingPhase}deg\n"
            final_str += f"*.SAT{satellite.satellite_id}.mobility.altitude = {satellite.altitude}km\n"
        # ----------------------      generate positions   ----------------------
        return writeFilePath, final_str

    def generateSRLinkConfig(self):
        """
        只进行物理链路的生成
        :return:
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/srConfig.xml"
        final_str = "<LinksConfig>\n"
        for satellite_id in self.project.constellation.nodeOwnLipsinLinksMap:
            # the key is the satellite id
            satellite_name = f"SAT{satellite_id}"
            final_str += f"\t<Router name='{satellite_name}'>\n\r"
            for link in self.project.constellation.nodeOwnLipsinLinksMap[satellite_id]:
                if link.lipsinLinkType == LipsinLink.LipsinLinkType.PHYSICAL_LINK:
                    final_str += (f"\t\t<PhysicalLink ifName='eth{link.sourceInterfaceIndex}'"
                                  f" srcId='{link.sourceSatelliteId}'"
                                  f" destId='{link.destinationSatelliteId}'"
                                  f" cost='{link.linkCost}'"
                                  f" linkId='{link.linkId}'"
                                  f" linkType='{link.linkType}'/>\n\r")
            final_str += "\t</Router>\n\r"
        final_str += "</LinksConfig>\n\r"
        return writeFilePath, final_str

    def generateAll(self):
        self.copyCrucialFiles()
        nedFilePath, nedFileContent = self.generateNedFile()
        iniFilePath, iniFileContent = self.generateIniFile()
        channelXmlWritePath, channelXmlContent = self.generateChannelXml()
        srnLinkConfigWritePath, srLinkConfigContent = self.generateSRLinkConfig()
        self.writeIntoFile(nedFilePath, nedFileContent)
        self.writeIntoFile(iniFilePath, iniFileContent)
        self.writeIntoFile(channelXmlWritePath, channelXmlContent)
        self.writeIntoFile(srnLinkConfigWritePath, srLinkConfigContent)
