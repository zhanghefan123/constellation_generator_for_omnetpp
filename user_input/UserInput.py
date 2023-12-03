import PyInquirer
import loguru
from pyfiglet import Figlet
from user_input import Questions
from modules import Constellation
from modules import Project
from modules import InterSatelliteLink
from generator import ScriptGeneratorFactory
from applications import LipsinApp


class UserInput:
    def __init__(self):
        """
        initialize the user interface
        """
        self.logger = loguru.logger
        self.answersForProject = None
        self.answersForConstellation = None
        self.answersForInterSatelliteLinks = None
        self.answersForRoutingProtocols = None

        self.answersForAddingLipsinApp = None
        self.answersForLipsinApp = None
        self.lipsin_apps = []

    def get_user_input(self) -> None:
        """
        get user input
        :return:  None
        """
        self.answersForProject = PyInquirer.prompt(questions=Questions.PROJECT_QUESTION)
        self.answersForConstellation = PyInquirer.prompt(questions=Questions.CONSTELLATION_QUESTION)
        self.answersForInterSatelliteLinks = PyInquirer.prompt(questions=Questions.LINK_QUESTION)
        self.answersForRoutingProtocols = PyInquirer.prompt(questions=Questions.ROUTING_PROTOCOL_QUESTION)
        self.get_lipsin_apps()

    def get_lipsin_apps(self):
        """
        get lipsin apps
        :return:  None
        """
        if self.answersForRoutingProtocols["protocol"] == "LIPSIN":
            self.answersForAddingLipsinApp = PyInquirer.prompt(questions=Questions.IF_ADD_LIPSIN_APP_QUESTION)
            if self.answersForAddingLipsinApp["add_or_not"] == "Yes":
                while True:
                    self.answersForLipsinApp = PyInquirer.prompt(questions=Questions.LIPSIN_APP_QUESTION)
                    source_satellite_id = self.answersForLipsinApp["source"]
                    destination_satellite_ids = []
                    for item in self.answersForLipsinApp["destinations"].split(","):
                        destination_satellite_ids.append(item)
                    lipsin_app = LipsinApp.LipsinApp(source_satellite_id, destination_satellite_ids)
                    self.lipsin_apps.append(lipsin_app)
                    self.logger.info(str(lipsin_app), "is added to the constellation.")
                    if self.answersForLipsinApp["continue"] == "Yes":
                        continue
                    else:
                        break

    def get_result(self) -> Project.Project:
        """
        get the result
        :return:  the project
        """
        # get project name
        projectName = self.answersForProject["project_name"]
        # get if check polar entering
        checkPolarEntering = self.answersForProject["check_polar_entering"]
        # get simulation time
        simTime = int(self.answersForProject["sim_time"])
        # get the type of the constellation
        constellationType = self.answersForConstellation["constellation_type"]
        # get constellation parameters
        orbitNumber = int(self.answersForConstellation["orbit_number"])
        satPerOrbit = int(self.answersForConstellation["sat_per_orbit"])
        inclination = float(self.answersForConstellation["inclination"])
        startingPhase = float(self.answersForConstellation["starting_phase"])
        altitude = float(self.answersForConstellation["altitude"])
        linkBandWidth = InterSatelliteLink.convert_str_to_bandwidth(self.answersForInterSatelliteLinks["bandwidth"])
        routingProtocol = Constellation.convert_str_to_routing_protocol(self.answersForRoutingProtocols["protocol"])
        # generate constellation
        self.logger.info("Generating constellation...")
        constellation = Constellation.Constellation(orbitNumber, satPerOrbit, inclination,
                                                    startingPhase, altitude, linkBandWidth,
                                                    routingProtocol, self.lipsin_apps, constellationType,
                                                    checkPolarEntering, simTime)
        # create project
        return Project.Project(projectName, constellation)

    # noinspection PyMethodMayBeStatic
    def create_logo(self) -> None:
        """
        create logo
        :return: None
        """
        f = Figlet(font='slant')
        print(f.renderText('Zeus Cons Gen'))

    def start(self):
        """
        start the user interface
        :return:  the project
        """
        self.create_logo()
        self.get_user_input()
        project = self.get_result()
        script_generator = ScriptGeneratorFactory.ScriptGeneratorFactory(project).create_generator()
        script_generator.generateAll()
        return project
