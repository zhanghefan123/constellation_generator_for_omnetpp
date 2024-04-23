from modules import Constellation as cm


class Project:
    def __init__(self, projectName: str, constellation: cm.Constellation):
        """
        initialize the project object
        :param projectName:  project name
        :param constellation:  constellation
        """
        self.projectName = projectName
        self.constellation = constellation

    def __str__(self):
        """
        print the project object
        :return:
        """
        return "Project Name: " + str(self.projectName) + "\n" + str(self.constellation)
