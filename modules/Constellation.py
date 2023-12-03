import math
from modules import Satellite, InterSatelliteLink, LipsinLink
from enum import Enum


def convert_str_to_routing_protocol(routingProtocolStr):
    if routingProtocolStr == "None":
        return Constellation.RoutingProtocols.NONE
    elif routingProtocolStr == "IP_OSPF":
        return Constellation.RoutingProtocols.IP_OSPF
    elif routingProtocolStr == "LIPSIN":
        return Constellation.RoutingProtocols.LIPSIN
    else:
        raise ValueError("Unknown routing protocol: " + routingProtocolStr)


class Constellation:
    class RoutingProtocols(Enum):
        """
        routing protocols
        """
        NONE = 0,
        IP_OSPF = 1,
        LIPSIN = 2,

        def __str__(self):
            return str(self.name)

    def __init__(self, orbitNumber, satPerOrbit, inclination,
                 startingPhase, altitude, linkBandWidth,
                 routingProtocol, lipsin_apps, constellation_type,
                 check_polar_entering, sim_time):
        """
        initialize the constellation object
        :param orbitNumber:  number of orbits
        :param satPerOrbit:  number of satellites per orbit
        :param inclination:  inclination
        :param startingPhase:  starting phase
        :param altitude:  altitude
        :param linkBandWidth:  bandwidth of inter satellite link
        :param routingProtocol:  the routing protocol on satellite
        :param constellation_type: the type of the constellation
        :param check_polar_entering: whether to check polar entering
        :param sim_time: simulation time
        """
        self.orbitNumber = orbitNumber
        self.satPerOrbit = satPerOrbit
        self.inclination = inclination
        self.startingPhase = startingPhase
        self.altitude = altitude
        self.linkBandWidth = linkBandWidth
        self.routingProtocol = routingProtocol
        self.lipsin_apps = lipsin_apps
        self.constellationType = constellation_type
        self.checkPolarEntering = check_polar_entering
        self.simTime = sim_time

        self.satellites = []  # all the satellites in the constellation
        self.ISLs = []  # no direction link
        self.LinksWithDirectionMap = {}  # single direction link
        self.constellationSatellitesGeneration()
        self.constellationInterSatelliteLinksGeneration()
        self.generateLinksWithDirectionMap()
        if self.routingProtocol == Constellation.RoutingProtocols.LIPSIN:
            self.nodeOwnLipsinLinksMap = {}  # node with its own lipsin links
            self.physicalLinkIdMap = {}  # map from (source_sat_id, dest_sat_id) to physical link id
            self.physicalLinksGeneration()
            self.virtualLinksGeneration()

    def constellationSatellitesGeneration(self):
        """
        generate the constellation
        :return:
        """
        if self.constellationType == "Walker_Star":
            angle = 180
            for orbitId in range(0, self.orbitNumber):
                for i in range(self.satPerOrbit * orbitId, self.satPerOrbit * (orbitId + 1)):
                    orbitNormal = [round(math.cos(orbitId * (angle / self.orbitNumber) * math.pi / 180), 4),
                                   round(math.sin(orbitId * (angle / self.orbitNumber) * math.pi / 180), 4),
                                   round(math.cos(self.inclination * math.pi / 180), 4)]
                    if orbitId & 1 == 0:  # 偶数
                        startingPhase = round((i - self.satPerOrbit * orbitId) * (360 / self.satPerOrbit), 4)
                    else:  # 奇数
                        startingPhase = round((i - self.satPerOrbit * orbitId + 0.5) * (360 / self.satPerOrbit), 4)

                    if orbitId * (angle / self.orbitNumber) >= 90:
                        startingPhase += 180
                        startingPhase %= 360
                    singleSatellite = Satellite.Satellite(i, orbitId, i % self.satPerOrbit,
                                                          [orbitNormal[0], orbitNormal[1], orbitNormal[2]],
                                                          startingPhase, self.altitude)
                    self.satellites.append(singleSatellite)
        elif self.constellationType == "Walker_Delta":
            angle = 360
            for orbitId in range(0, self.orbitNumber):
                for i in range(self.satPerOrbit * orbitId, self.satPerOrbit * (orbitId + 1)):
                    # 轨道范数
                    orbitNormal = [round(math.cos(orbitId * (angle / self.orbitNumber) * math.pi / 180), 4),
                                   round(math.sin(orbitId * (angle / self.orbitNumber) * math.pi / 180), 4),
                                   round(math.cos(self.inclination * math.pi / 180), 4)]
                    if orbitId & 1 == 0:  # 偶数
                        startingPhase = round((i - self.satPerOrbit * orbitId) * (360 / self.satPerOrbit), 4)
                    else:
                        startingPhase = round((i - self.satPerOrbit * orbitId + 0.5) * (360 / self.satPerOrbit), 4)
                    singleSatellite = Satellite.Satellite(i, orbitId, i % self.satPerOrbit,
                                                          [orbitNormal[0], orbitNormal[1], orbitNormal[2]],
                                                          startingPhase, self.altitude)
                    self.satellites.append(singleSatellite)

    def constellationInterSatelliteLinksGeneration(self):
        """
        generate the constellation links
        :return:
        """
        if self.constellationType == "Walker_Star":
            # traverse all the satellites
            for singleSatellite in self.satellites:
                sourceOrbitId = singleSatellite.orbit_id
                sourceIndexInOrbit = singleSatellite.index_in_orbit
                sourceIndex = singleSatellite.satellite_id
                destOrbitId = sourceOrbitId  # in the same orbit
                destIndexInOrbit = (sourceIndexInOrbit + 1) % self.satPerOrbit  # next satellite index in the same orbit
                destIndex = destOrbitId * self.satPerOrbit + destIndexInOrbit  # next satellite id
                # create the intra-orbit-isl
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                self.linkBandWidth,
                                                                InterSatelliteLink.InterSatelliteLink.LinkType.INTRA_ORBIT)
                self.satellites[sourceIndex].interfaceIndex += 1
                self.satellites[destIndex].interfaceIndex += 1
                self.ISLs.append(linkTmp)
                # create the inter-orbit-isl
                destOrbitId = sourceOrbitId + 1  # next orbit
                destIndexInOrbit = sourceIndexInOrbit  # same index in the next orbit
                if destOrbitId < self.orbitNumber:
                    destIndex = destOrbitId * self.satPerOrbit + destIndexInOrbit
                    linkId = len(self.ISLs)
                    linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                    self.satellites[sourceIndex].interfaceIndex,
                                                                    self.satellites[destIndex],
                                                                    self.satellites[destIndex].interfaceIndex,
                                                                    self.linkBandWidth,
                                                                    InterSatelliteLink.InterSatelliteLink.LinkType.
                                                                    INTER_ORBIT)
                    self.satellites[sourceIndex].interfaceIndex += 1
                    self.satellites[destIndex].interfaceIndex += 1
                    self.ISLs.append(linkTmp)
        elif self.constellationType == "Walker_Delta":
            # traverse all the satellites
            for singleSatellite in self.satellites:
                sourceOrbitId = singleSatellite.orbit_id
                sourceIndexInOrbit = singleSatellite.index_in_orbit
                sourceIndex = singleSatellite.satellite_id
                destOrbitId = sourceOrbitId  # first create link in the same orbit
                destIndexInOrbit = (sourceIndexInOrbit + 1) % self.satPerOrbit  # next satellite index in the same orbit
                destIndex = destOrbitId * self.satPerOrbit + destIndexInOrbit  # next satellite id
                # create the intra-orbit-isl
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                self.linkBandWidth,
                                                                InterSatelliteLink.InterSatelliteLink.LinkType.INTRA_ORBIT)
                self.satellites[sourceIndex].interfaceIndex += 1
                self.satellites[destIndex].interfaceIndex += 1
                self.ISLs.append(linkTmp)
                # create the inter-orbit-isl
                destOrbitId = sourceOrbitId + 1
                # same index in the next orbit
                destIndexInOrbit = sourceIndexInOrbit
                if destOrbitId < self.orbitNumber:
                    destIndex = destOrbitId * self.satPerOrbit + destIndexInOrbit
                    linkId = len(self.ISLs)
                    linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                    self.satellites[sourceIndex].interfaceIndex,
                                                                    self.satellites[destIndex],
                                                                    self.satellites[destIndex].interfaceIndex,
                                                                    self.linkBandWidth,
                                                                    InterSatelliteLink.InterSatelliteLink.LinkType.
                                                                    INTER_ORBIT)
                    self.satellites[sourceIndex].interfaceIndex += 1
                    self.satellites[destIndex].interfaceIndex += 1
                    self.ISLs.append(linkTmp)

            # calculate the inter-orbit links among the first and last orbit ISLs
            for sourceIndex in range(0, self.satPerOrbit):
                destIndex = (self.orbitNumber - 1) * self.satPerOrbit + sourceIndex
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                self.linkBandWidth,
                                                                InterSatelliteLink.InterSatelliteLink.LinkType.
                                                                INTER_ORBIT)
                self.satellites[sourceIndex].interfaceIndex += 1
                self.satellites[destIndex].interfaceIndex += 1
                self.ISLs.append(linkTmp)

    def physicalLinksGeneration(self):
        physicalLinkId = 1
        linkCost = 1
        # link map
        # traverse all the ISLs
        for sourceAndDest in self.LinksWithDirectionMap:
            singleDirectionLink = self.LinksWithDirectionMap[sourceAndDest]
            # positive order
            # ---------------------------------------------------------------------------------------------------
            newPositivePhysicalLink = LipsinLink.LipsinLink(physicalLinkId,
                                                            LipsinLink.LipsinLinkType.PHYSICAL_LINK,
                                                            singleDirectionLink.sourceInterfaceIndex,
                                                            singleDirectionLink.sourceSatellite.satellite_id,
                                                            singleDirectionLink.destinationSatellite.satellite_id,
                                                            linkCost,  # linkCost is set to 1 by default
                                                            singleDirectionLink.linkType)
            if singleDirectionLink.sourceSatellite.satellite_id not in self.nodeOwnLipsinLinksMap:
                self.nodeOwnLipsinLinksMap[singleDirectionLink.sourceSatellite.satellite_id] = [
                    newPositivePhysicalLink]
            else:
                self.nodeOwnLipsinLinksMap[singleDirectionLink.sourceSatellite.satellite_id].append(
                    newPositivePhysicalLink)
            self.physicalLinkIdMap[(singleDirectionLink.sourceSatellite.satellite_id,
                                    singleDirectionLink.destinationSatellite.satellite_id)] = physicalLinkId
            physicalLinkId += 1
            # ---------------------------------------------------------------------------------------------------

    def getPreviousSatelliteIndex(self, satellite_id):
        satellite_per_orbit = self.satPerOrbit
        orbit_id = int(satellite_id / satellite_per_orbit)
        return (satellite_id + satellite_per_orbit - 1) % satellite_per_orbit + orbit_id * satellite_per_orbit

    def getNextSatelliteIndex(self, satellite_id):
        satellite_per_orbit = self.satPerOrbit
        orbit_id = int(satellite_id / satellite_per_orbit)
        return (satellite_id + 1) % satellite_per_orbit + orbit_id * satellite_per_orbit

    def generateLinksWithDirectionMap(self):
        # we need to traverse all the ISLs
        for interSatelliteLink in self.ISLs:
            # add from source -> destination link
            source_sat_id = interSatelliteLink.sourceSatellite.satellite_id
            dest_sat_id = interSatelliteLink.destinationSatellite.satellite_id
            self.LinksWithDirectionMap[(source_sat_id, dest_sat_id)] = interSatelliteLink
            # create from destination -> source link
            reverseDirectionLink = InterSatelliteLink.InterSatelliteLink(interSatelliteLink.linkId,
                                                                         interSatelliteLink.destinationSatellite,
                                                                         interSatelliteLink.destInterfaceIndex,
                                                                         interSatelliteLink.sourceSatellite,
                                                                         interSatelliteLink.sourceInterfaceIndex,
                                                                         interSatelliteLink.bandWidth,
                                                                         interSatelliteLink.linkType)
            self.LinksWithDirectionMap[(dest_sat_id, source_sat_id)] = reverseDirectionLink

    def virtualLinksGeneration(self):
        """
        virtual links generation
        :return:
        """
        # traverse all the inter satellite links
        for sourceAndDest in self.LinksWithDirectionMap:
            singleDirectionLink = self.LinksWithDirectionMap[sourceAndDest]
            # we don't need to generate virtual links for intra orbit links
            if singleDirectionLink.linkType == InterSatelliteLink.InterSatelliteLink.LinkType.INTRA_ORBIT:
                continue
            # we need to generate virtual links for inter orbit links
            # get the link id
            link_id = self.physicalLinkIdMap[(singleDirectionLink.sourceSatellite.satellite_id,
                                              singleDirectionLink.destinationSatellite.satellite_id)]
            # set default link cost
            link_cost = 1
            # get source satellite id
            source_sat_id = singleDirectionLink.sourceSatellite.satellite_id
            # get destination satellite id
            dest_sat_id = singleDirectionLink.destinationSatellite.satellite_id
            # get source and dest previous satellite
            source_previous_id = self.getPreviousSatelliteIndex(source_sat_id)
            dest_previous_id = self.getPreviousSatelliteIndex(dest_sat_id)
            # get source and dest next satellite
            source_next_id = self.getNextSatelliteIndex(source_sat_id)
            dest_next_id = self.getNextSatelliteIndex(dest_sat_id)
            # split the situation to discuss
            # the first situation: source satellite on the left and dest satellite on the right
            if source_sat_id < dest_sat_id:
                first_link_interface_index = self.LinksWithDirectionMap[
                    (source_sat_id, source_previous_id)].sourceInterfaceIndex
                first_up_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                              first_link_interface_index,
                                                              source_sat_id, dest_sat_id, link_cost,
                                                              singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[source_sat_id].append(first_up_virtual_link)

                second_right_interface_index = self.LinksWithDirectionMap[
                    (source_previous_id, dest_previous_id)].sourceInterfaceIndex
                second_right_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                                  second_right_interface_index,
                                                                  source_sat_id, dest_sat_id, link_cost,
                                                                  singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[source_previous_id].append(second_right_virtual_link)

                third_link_interface_index = self.LinksWithDirectionMap[
                    (dest_previous_id, dest_sat_id)].sourceInterfaceIndex
                third_down_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                                third_link_interface_index,
                                                                source_sat_id, dest_sat_id, link_cost,
                                                                singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[dest_previous_id].append(third_down_virtual_link)
            else:
                # the second situation: source satellite on the right and dest satellite on the left
                first_link_interface_index = self.LinksWithDirectionMap[
                    (source_sat_id, source_next_id)].sourceInterfaceIndex
                first_down_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                                first_link_interface_index,
                                                                source_sat_id, dest_sat_id, link_cost,
                                                                singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[source_sat_id].append(first_down_virtual_link)

                second_left_interface_index = self.LinksWithDirectionMap[
                    (source_next_id, dest_next_id)].sourceInterfaceIndex
                second_left_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                                 second_left_interface_index,
                                                                 source_sat_id, dest_sat_id, link_cost,
                                                                 singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[source_next_id].append(second_left_virtual_link)

                third_link_interface_index = self.LinksWithDirectionMap[
                    (dest_next_id, dest_sat_id)].sourceInterfaceIndex
                third_up_virtual_link = LipsinLink.LipsinLink(link_id, LipsinLink.LipsinLinkType.VIRTUAL_LINK,
                                                              third_link_interface_index,
                                                              source_sat_id, dest_sat_id, link_cost,
                                                              singleDirectionLink.linkType)
                self.nodeOwnLipsinLinksMap[dest_next_id].append(third_up_virtual_link)

    def __str__(self):
        """
        to string magic method
        :return:
        """
        finalStr = ""
        finalStr += "orbitNumber: " + str(self.orbitNumber) + "\n"
        finalStr += "satPerOrbit: " + str(self.satPerOrbit) + "\n"
        finalStr += "inclination: " + str(self.inclination) + "\n"
        finalStr += "startingPhase: " + str(self.startingPhase) + "\n"
        finalStr += "altitude: " + str(self.altitude) + "\n"
        finalStr += "routingProtocol: " + str(self.routingProtocol) + "\n"
        finalStr += "satellites: " + "\n"
        for satellite in self.satellites:
            finalStr += str(satellite) + "\n"
        finalStr += "ISLs: " + "\n"
        for isl in self.ISLs:
            finalStr += str(isl) + "\n"
        return finalStr
