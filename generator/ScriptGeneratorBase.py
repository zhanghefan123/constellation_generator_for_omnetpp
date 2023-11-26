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
                          f"channel-type='projects.{self.project.projectName}."
                          f"OsgEarthNet.{self.project.constellation.linkBandWidth}' "
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
