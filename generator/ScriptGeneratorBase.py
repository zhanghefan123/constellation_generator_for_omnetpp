from typing import Tuple
from global_vars import GlobalVars
from tools import Tools
import os


class ScriptGeneratorBase:
    def __init__(self, project):
        self.project = project

    def generateNedFile(self):
        raise NotImplementedError

    def generateIniFile(self):
        raise NotImplementedError

    def generateAll(self):
        raise NotImplementedError

    def checkPolarAreaEntering(self) -> str:
        # check polar entering or not
        if self.project.constellation.checkPolarEntering == "Yes":
            return "OsgEarthNet.channelController.checkPolarEnter = true\n"
        else:
            return "OsgEarthNet.channelController.checkPolarEnter = false\n"

    # noinspection PyMethodMayBeStatic
    def generateAddressXml(self) -> Tuple[str, str]:
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/address.xml"
        final_str = "<config>\n\r"
        final_str += "\t<interface among='**' address='10.x.x.x' netmask='255.255.255.252'/>\n\r"
        final_str += "</config>\n\r"
        return writeFilePath, final_str

    def generateChannelXml(self) -> Tuple[str, str]:
        writeFilePath = f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/projects/{self.project.projectName}/channel.xml"
        final_str = "<config>\n\r"
        for interSatelliteLink in self.project.constellation.ISLs:
            final_str += (f"\t<SatToSat src-module='SAT{interSatelliteLink.sourceSatellite.satellite_id}' "
                          f"src-gate='ethg[{interSatelliteLink.sourceInterfaceIndex}]' "
                          f"dest-module='SAT{interSatelliteLink.destinationSatellite.satellite_id}' "
                          f"dest-gate='ethg[{interSatelliteLink.destInterfaceIndex}]' "
                          f"channel-type='nedFiles.channels.{interSatelliteLink.bandWidth}' "
                          f"link-info='{interSatelliteLink.linkType}'"
                          f"/>\n\r")
        final_str += "</config>\n\r"
        return writeFilePath, final_str

    def copyCrucialFiles(self):
        source_of_crucial_files = "resources/crucial_files/"
        # first we need to check the existence of the destination folder
        destination_of_crucial_files = (f"{GlobalVars.MULTILAYER_SATELLITES_PATH}/"
                                        f"projects/{self.project.projectName}/")
        if not os.path.exists(destination_of_crucial_files):
            os.system(f"mkdir -p {destination_of_crucial_files}")
        # then we copy the files
        os.system(f"cp {source_of_crucial_files}* {destination_of_crucial_files}")

    # noinspection PyMethodMayBeStatic
    def writeIntoFile(self, file_path, content) -> None:
        """
        write content into file
        :param file_path:  the path of the file
        :param content:  the content of the file
        :return:  None
        """
        directory_path = Tools.Tools.get_dir_path(file_path)
        if not os.path.exists(directory_path):
            os.system(f"mkdir -p {directory_path}")
        # if the file doesn't exist create and write
        with open(file_path, "w") as writer:
            writer.write(content)

    def generateGslType(self) -> str:
        """
        generate gsl type
        :return: the gsl type
        """
        gslType = self.project.constellation.gslLinkBandWidth
        result = f"gslType=\"nedFiles.channels.{str(gslType)}\""
        return result

    def generateSatelliteNumberNedPar(self) -> str:
        """
        generate satellite number ini par
        :return:
        """
        numberOfSatellites = len(self.project.constellation.satellites)
        result = "satelliteNum=" + str(numberOfSatellites)
        return result

    def generateGroundStationNumberNedPar(self) -> str:
        """
        generate ground station number ini par
        :return:
        """
        numberOfGroundStations = len(self.project.constellation.groundStations)
        result = "groundStationNum=" + str(numberOfGroundStations)
        return result

    def generateChannelControllerNed(self) -> str:
        """
        generate channel controller ned
        :return:
        """
        result = ""
        result += f"\t\tchannelController: ChannelController" + "{\n\r"
        result += f"\t\t\tparameters:\n\r"
        result += f"\t\t\t\tconfig=xmldoc(\"./channel.xml\");\n\r"
        result += f"\t\t\t\t{self.generateGslType()};\n\r"
        result += f"\t\t\t\t{self.generateSatelliteNumberNedPar()};\n\r"
        result += f"\t\t\t\t{self.generateGroundStationNumberNedPar()};\n\r"
        result += "\t\t}\n\r"
        return result

    def generateSimTimeIni(self) -> str:
        """
        generate simtime ini par
        :return:
        """
        simTime = self.project.constellation.simTime
        result = "sim-time-limit=" + str(simTime) + "s" + "\n"
        return result

    def generateGroundStationNed(self) -> str:
        """
        generate ground station ned
        :return: the ned content
        """
        result = ""
        for index, ground_station in enumerate(self.project.constellation.groundStations):
            result += f"\t\tGND{index}: GroundCommNode" + "{\n\r"
            result += "\t\t}\n\r"
        return result

    def generateGroundStationIni(self) -> str:
        """
        generate ground station ini
        :return: the ini content
        """
        result = ""
        for index, ground_station in enumerate(self.project.constellation.groundStations):
            result += f"*.GND{index}.mobility.label = \"{ground_station.name}\"\n"
            result += f"*.GND{index}.mobility.longitude = {ground_station.longitude}\n"
            result += f"*.GND{index}.mobility.latitude = {ground_station.latitude}\n"
            result += f"*.GND{index}.mobility.altitude = 0km\n"
        return result
