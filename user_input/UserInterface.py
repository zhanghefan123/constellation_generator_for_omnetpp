from tools import config_reader as crm
from modules import Constellation as cm
from modules import Project as pm
from generator import ScriptGeneratorFactory as sgfm


class UserInterface:
    def __init__(self):
        self.config_reader = crm.ConfigReader()

    def start(self):
        self.config_reader.start()
        constellation = cm.Constellation(config_reader=self.config_reader)
        project = pm.Project(projectName=self.config_reader.project_name, constellation=constellation)
        script_generator = sgfm.ScriptGeneratorFactory(project).create_generator()
        script_generator.generateAll()
