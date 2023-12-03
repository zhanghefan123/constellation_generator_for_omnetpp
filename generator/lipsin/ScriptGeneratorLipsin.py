from typing import Tuple
from generator import ScriptGeneratorBase
from global_vars import GlobalVars
from modules import LipsinLink


class ScriptGeneratorLipsin(ScriptGeneratorBase.ScriptGeneratorBase):
    def __init__(self, project):
        super().__init__(project)

    def generateNedFile(self) -> Tuple[str, str]:
        """
        generate ned file
        :return:
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/OsgEarthNet.ned"
        final_str = f"package projects.{self.project.projectName};\n"
        # preload file
        with open("resources/lipsin/ned_pre_file") as reader:
            final_str += reader.read()
        # write the LipsinGlobalRecorder
        final_str += self.generateChannelControllerNed()
        final_str += f"\t\tlipsinGlobalRecorder: LipsinGlobalRecorder" + "{\n\r"
        final_str += f"\t\t\tparameters:\n\r"
        final_str += f"\t\t\t\t{self.generateSatelliteNumberNedPar()}"
        final_str += "\t\t}\n\r"
        # add satellite modules
        for satellite in self.project.constellation.satellites:
            final_str += f"\t\tSAT{satellite.satellite_id}: {GlobalVars.LIPSIN_SATELLITE_MODULE_NAME}" + "{\n\r"
            final_str += f"\t\t\tparameters:\n\r"
            final_str += f"\t\t\t\tislInterfaceCount = {satellite.interfaceCount};\n\r"
            final_str += f"\t\t\t\tgslInterfaceCount = {self.project.constellation.extraGslInterfaceCount};\n\r"
            append_x = 0
            if satellite.index_in_orbit == 0 or (satellite.index_in_orbit == self.project.constellation.satPerOrbit - 1):
                append_x = 50
            final_str += f'''\t\t\t\t@display("p={100 + 150*satellite.orbit_id + append_x},{100 + 100*satellite.index_in_orbit}");\n\r'''
            final_str += f"\t\t\tgates:\n\r"
            final_str += f"\t\t\t\tethg[{satellite.interfaceIndex + self.project.constellation.extraGslInterfaceCount}];\n\r"
            final_str += f"\t\t" + "}" + "\n\r"
        final_str += "\t connections allowunconnected:\n\r"
        # add connections
        for interSatelliteLink in self.project.constellation.ISLs:
            final_str += (f"\t\tSAT{interSatelliteLink.sourceSatellite.satellite_id}"
                          f".ethg[{interSatelliteLink.sourceInterfaceIndex}]"
                          f" <--> "
                          f"{self.project.constellation.linkBandWidth}"
                          f" <--> "
                          f"SAT{interSatelliteLink.destinationSatellite.satellite_id}"
                          f".ethg[{interSatelliteLink.destInterfaceIndex}];\n\r")
        final_str += "}"
        return writeFilePath, final_str

    def generateIniFile(self):
        """
        generate ini file
        :return:
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/Starter.ini"
        final_str = "[General]\n"
        final_str += "network = OsgEarthNet\n"
        # preload file
        with open("resources/lipsin/ini_pre_file") as f:
            final_str += f.read()
        # generate simtime
        self.generateSimTimeIni()
        # generate whether to check polar entering
        final_str += self.checkPolarAreaEntering()
        # generate satellites position
        for satellite in self.project.constellation.satellites:
            # noinspection
            final_str += f"""*.SAT{satellite.satellite_id}.mobility.orbitNormal = \"{satellite.orbitNorms[0]}, {satellite.orbitNorms[1]}, {satellite.orbitNorms[2]}\"\n"""
            final_str += f"*.SAT{satellite.satellite_id}.mobility.startingPhase = {satellite.startingPhase}deg\n"
            final_str += f"*.SAT{satellite.satellite_id}.mobility.altitude = {satellite.altitude}km\n"
        return writeFilePath, final_str

    def generateLipsinLinkConfig(self):
        """
        generate lipsin link config
        :return:
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/lipsinConfig.xml"
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
                else:
                    final_str += (f"\t\t<VirtualLink ifName='eth{link.sourceInterfaceIndex}'"
                                  f" srcId='{link.sourceSatelliteId}'"
                                  f" destId='{link.destinationSatelliteId}'"
                                  f" cost='{link.linkCost}'"
                                  f" linkId='{link.linkId}'/>\n\r")
            final_str += "\t</Router>\n\r"
        final_str += "</LinksConfig>\n\r"
        return writeFilePath, final_str

    def generateApps(self):
        """
        generate lipsin apps
        :return:  the lipsin apps
        """
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/destinationSatellites.xml"
        final_str = "<Satellites>\n"
        # traverse the lipsin apps
        for lipsin_app in self.project.constellation.lipsin_apps:
            final_str += f"\t<Satellite id='{lipsin_app.source}'>\n\r"
            # traverse the destinations in the lipsin app
            for destination in lipsin_app.destinations:
                final_str += f"\t\t<Destination>{destination}</Destination>\n\r"
            final_str += "\t</Satellite>\n\r"
        final_str += "</Satellites>\n\r"
        return writeFilePath, final_str

    def generateAll(self):
        self.copyCrucialFiles()
        nedFilePath, nedFileContent = self.generateNedFile()
        iniFilePath, iniFileContent = self.generateIniFile()
        channelXmlWritePath, channelXmlContent = self.generateChannelXml()
        lipsinLinkConfigWritePath, lipsinLinkConfigContent = self.generateLipsinLinkConfig()
        lipsinAppWritePath, lipsinAppContent = self.generateApps()
        self.writeIntoFile(nedFilePath, nedFileContent)
        self.writeIntoFile(iniFilePath, iniFileContent)
        self.writeIntoFile(channelXmlWritePath, channelXmlContent)
        self.writeIntoFile(lipsinLinkConfigWritePath, lipsinLinkConfigContent)
        self.writeIntoFile(lipsinAppWritePath, lipsinAppContent)
