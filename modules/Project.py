class Project:
    def __init__(self, projectName, constellation):
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
