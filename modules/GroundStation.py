class GroundStation:
    def __init__(self, name, latitude, longitude):
        """
        initialize the ground station
        :param name:  the name of the ground station
        :param latitude:  the latitude of the ground station
        :param longitude:  the longitude of the ground station
        """
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return ("GroundStation: name: " + str(self.name)
                + ", latitude: " + str(self.latitude) +
                ", longitude: " + str(self.longitude))
