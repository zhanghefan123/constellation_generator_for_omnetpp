class Satellite:
    def __init__(self, satellite_id, orbit_id, index_in_orbit, orbitNorms, startingPhase, altitude):
        """
        initialize the satellite object
        :param satellite_id: satellite id
        :param orbit_id: orbit id
        :param index_in_orbit: index in its orbit
        :param orbitNorms: three orbit norms
        :param startingPhase: starting phase
        :param altitude: altitude
        """
        self.satellite_id = satellite_id
        self.orbit_id = orbit_id
        self.index_in_orbit = index_in_orbit
        self.orbitNorms = orbitNorms
        self.startingPhase = startingPhase
        self.altitude = altitude
        self.interfaceIndex = 0
        self.area = None  # 卫星所处的区域

    def __str__(self):
        """
        print the satellite object
        :return:
        """
        return "Satellite: " + str(self.satellite_id) + " Orbit: " + str(self.orbit_id) + " Index: " + str(
            self.index_in_orbit) + " Orbit Norms: " + str(self.orbitNorms) + " Starting Phase: " + str(
            self.startingPhase) + " Altitude: " + str(self.altitude)
