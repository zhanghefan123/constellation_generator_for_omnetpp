from typing import Tuple
from generator import ScriptGeneratorBase
from global_vars import GlobalVars


class ScriptGeneratorOspf(ScriptGeneratorBase.ScriptGeneratorBase):
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
        with open("resources/ospf/ned_pre_file") as reader:
            final_str += reader.read()
        # add satellite modules
        for satellite in self.project.constellation.satellites:
            final_str += f"\t\tSAT{satellite.satellite_id}: {GlobalVars.OSPF_SATELLITE_MODULE_NAME}" + "{\n\r"
            final_str += f"\t\t\tparameters:\n\r"
            final_str += f"\t\t\t\thasOspf = true;\n\r"
            final_str += f"\t\t\tgates:\n\r"
            final_str += f"\t\t\t\tethg[{satellite.interfaceIndex + self.project.constellation.extraGslInterfaceCount}];\n\r"
            final_str += f"\t\t" + "}" + "\n\r"
        final_str += "\t connections allowunconneted:\n\r"
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

    def generateIniFile(self) -> Tuple[str, str]:
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/Starter.ini"
        final_str = "[General]\n"
        final_str += "network = OsgEarthNet\n"
        # preload file
        with open("resources/ospf/ini_pre_file") as f:
            final_str += f.read()
        # generate satellite number config
        final_str += self.generateSatelliteNumberIniPar()
        # generate whether to check polar entering
        final_str += self.checkPolarAreaEntering()
        # generate satellites position
        for satellite in self.project.constellation.satellites:
            # noinspection
            final_str += f"""*.SAT{satellite.satellite_id}.mobility.orbitNormal = \"{satellite.orbitNorms[0]}, {satellite.orbitNorms[1]}, {satellite.orbitNorms[2]}\"\n"""
            final_str += f"*.SAT{satellite.satellite_id}.mobility.startingPhase = {satellite.startingPhase}deg\n"
            final_str += f"*.SAT{satellite.satellite_id}.mobility.altitude = {satellite.altitude}km\n"
        return writeFilePath, final_str

    def generateOspfConfigXml(self) -> Tuple[str, str]:
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/ospf_config.xml"
        area_id = "0.0.0.0"
        interface_output_cost = "1"
        final_str = "<OSPFASConfig>\n"
        for satellite in self.project.constellation.satellites:
            final_str += f"\t<Router name='SAT{satellite.satellite_id}' RFC1583Compatible='true'>\n"
            for satellite_interface in range(satellite.interfaceIndex):
                final_str += (f"\t\t<PointToPointInterface ifName='eth{satellite_interface}' "
                              f"areaID='{area_id}' interfaceOutputCost='{interface_output_cost}'/> \n\r")
            final_str += "\t</Router>\n"
        final_str += "</OSPFASConfig>\n"
        return writeFilePath, final_str

    def generateAll(self):
        """
        generate all files
        :return:
        """
        # this operation will copy the crucial files
        self.copyCrucialFiles()
        nedFileWritePath, nedFileContent = self.generateNedFile()
        iniFileWritePath, iniFileContent = self.generateIniFile()
        ospfConfigXmlWritePath, ospfConfigXmlContent = self.generateOspfConfigXml()
        addressXmlWritePath, addressXmlContent = self.generateAddressXml()
        channelXmlWritePath, channelXmlContent = self.generateChannelXml()
        self.writeIntoFile(nedFileWritePath, nedFileContent)
        self.writeIntoFile(iniFileWritePath, iniFileContent)
        self.writeIntoFile(ospfConfigXmlWritePath, ospfConfigXmlContent)
        self.writeIntoFile(addressXmlWritePath, addressXmlContent)
        self.writeIntoFile(channelXmlWritePath, channelXmlContent)
