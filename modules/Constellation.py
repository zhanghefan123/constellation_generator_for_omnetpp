import math
from tools import config_reader as crm
from modules import Satellite, InterSatelliteLink, LipsinLink
from modules import ModuleTypes as mtm


class Constellation:

    def __init__(self, config_reader: crm.ConfigReader):
        """
        initialize the constellation object
        """
        self.config_reader = config_reader
        self.ground_stations = config_reader.ground_stations
        self.lipsin_apps = config_reader.lipsin_apps
        self.satellites = []  # all the satellites in the constellation
        self.ISLs = []  # no direction link
        self.LinksWithDirectionMap = {}  # single direction link
        self.constellationSatellitesGeneration()
        self.constellationInterSatelliteLinksGeneration()
        self.generateLinksWithDirectionMap()
        if self.config_reader.routing_protocol == mtm.RoutingProtocols.LIPSIN:
            self.nodeOwnLipsinLinksMap = {}  # node with its own lipsin links
            self.physicalLinkIdMap = {}  # map from (source_sat_id, dest_sat_id) to physical link id
            self.physicalLinksGeneration()
            self.virtualLinksGeneration()
        elif self.config_reader.routing_protocol == mtm.RoutingProtocols.SR:
            self.nodeOwnLipsinLinksMap = {}
            self.physicalLinkIdMap = {}
            self.physicalLinksGeneration()  # SR 仅仅需要生成的是物理链路就行了，而不需要进行虚拟链路的生成

    def constellationSatellitesGeneration(self):
        """
        generate the constellation
        :return:
        """
        orbit_number = self.config_reader.orbit_number
        sat_per_orbit = self.config_reader.sat_per_orbit
        inclination = self.config_reader.inclination
        altitude = self.config_reader.altitude
        if self.config_reader.constellation_type == mtm.ConstellationType.WALKER_STAR:
            angle = 180
            for orbitId in range(0, orbit_number):
                for i in range(sat_per_orbit * orbitId, sat_per_orbit * (orbitId + 1)):
                    orbitNormal = [round(math.cos(orbitId * (angle / orbit_number) * math.pi / 180), 4),
                                   round(math.sin(orbitId * (angle / orbit_number) * math.pi / 180), 4),
                                   round(math.cos(inclination * math.pi / 180), 4)]
                    if orbitId & 1 == 0:  # 偶数
                        startingPhase = round((i - sat_per_orbit * orbitId) * (360 / sat_per_orbit), 4)
                    else:  # 奇数
                        startingPhase = round((i - sat_per_orbit * orbitId + 0.5) * (360 / sat_per_orbit), 4)

                    if orbitId * (angle / orbit_number) >= 90:
                        startingPhase += 180
                        startingPhase %= 360
                    singleSatellite = Satellite.Satellite(i, orbitId, i % sat_per_orbit,
                                                          [orbitNormal[0], orbitNormal[1], orbitNormal[2]],
                                                          startingPhase, altitude)
                    self.satellites.append(singleSatellite)
        elif self.config_reader.constellation_type == mtm.ConstellationType.WALKER_DELTA:
            angle = 360
            for orbitId in range(0, orbit_number):
                for i in range(sat_per_orbit * orbitId, sat_per_orbit * (orbitId + 1)):
                    # 轨道范数
                    orbitNormal = [round(math.cos(orbitId * (angle / orbit_number) * math.pi / 180), 4),
                                   round(math.sin(orbitId * (angle / orbit_number) * math.pi / 180), 4),
                                   round(math.cos(inclination * math.pi / 180), 4)]
                    if orbitId & 1 == 0:  # 偶数
                        startingPhase = round((i - sat_per_orbit * orbitId) * (360 / sat_per_orbit), 4)
                    else:
                        startingPhase = round((i - sat_per_orbit * orbitId + 0.5) * (360 / sat_per_orbit), 4)
                    singleSatellite = Satellite.Satellite(i, orbitId, i % sat_per_orbit,
                                                          [orbitNormal[0], orbitNormal[1], orbitNormal[2]],
                                                          startingPhase, altitude)
                    self.satellites.append(singleSatellite)
        # =============== generate corresponding area for satellite ===============
        vertical_areas = sat_per_orbit / self.config_reader.area_sat_per_orbit
        for orbitId in range(0, orbit_number):
            for i in range(sat_per_orbit * orbitId, sat_per_orbit * (orbitId + 1)):
                horizontal_area_index = (orbitId // self.config_reader.area_orbit_count) * vertical_areas
                vertical_area_index = (i % sat_per_orbit) // self.config_reader.area_sat_per_orbit
                area_id = horizontal_area_index + vertical_area_index
                self.satellites[i].area = int(area_id + 1)
        for line in range(0, sat_per_orbit):
            for column in range(0, orbit_number):
                satellite_index = column * sat_per_orbit + line
                if column != (orbit_number - 1):
                    print(f"{satellite_index}: {self.satellites[satellite_index].area}", end=",")
                else:
                    print(f"{satellite_index}: {self.satellites[satellite_index].area}", end="")
            print()
        # =============== generate corresponding area for satellite ===============

    def constellationInterSatelliteLinksGeneration(self):
        """
        generate the constellation links
        :return:
        """
        constellation_type = self.config_reader.constellation_type
        sat_per_orbit = self.config_reader.sat_per_orbit
        isl_band_width = self.config_reader.isl_link_bandwidth
        orbit_number = self.config_reader.orbit_number
        if constellation_type == mtm.ConstellationType.WALKER_STAR:
            # traverse all the satellites
            for singleSatellite in self.satellites:
                sourceOrbitId = singleSatellite.orbit_id
                sourceIndexInOrbit = singleSatellite.index_in_orbit
                sourceIndex = singleSatellite.satellite_id
                destOrbitId = sourceOrbitId  # in the same orbit
                destIndexInOrbit = (sourceIndexInOrbit + 1) % sat_per_orbit  # next satellite index in the same orbit
                destIndex = destOrbitId * sat_per_orbit + destIndexInOrbit  # next satellite id
                # create the intra-orbit-isl
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                isl_band_width,
                                                                InterSatelliteLink.InterSatelliteLink.LinkType.INTRA_ORBIT)
                self.satellites[sourceIndex].interfaceIndex += 1
                self.satellites[destIndex].interfaceIndex += 1
                self.ISLs.append(linkTmp)
                # create the inter-orbit-isl
                destOrbitId = sourceOrbitId + 1  # next orbit
                destIndexInOrbit = sourceIndexInOrbit  # same index in the next orbit
                if destOrbitId < orbit_number:
                    destIndex = destOrbitId * sat_per_orbit + destIndexInOrbit
                    linkId = len(self.ISLs)
                    linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                    self.satellites[sourceIndex].interfaceIndex,
                                                                    self.satellites[destIndex],
                                                                    self.satellites[destIndex].interfaceIndex,
                                                                    isl_band_width,
                                                                    InterSatelliteLink.InterSatelliteLink.LinkType.
                                                                    INTER_ORBIT)
                    self.satellites[sourceIndex].interfaceIndex += 1
                    self.satellites[destIndex].interfaceIndex += 1
                    self.ISLs.append(linkTmp)
        elif constellation_type == mtm.ConstellationType.WALKER_DELTA:
            # traverse all the satellites
            for singleSatellite in self.satellites:
                sourceOrbitId = singleSatellite.orbit_id
                sourceIndexInOrbit = singleSatellite.index_in_orbit
                sourceIndex = singleSatellite.satellite_id
                destOrbitId = sourceOrbitId  # first create link in the same orbit
                destIndexInOrbit = (sourceIndexInOrbit + 1) % sat_per_orbit  # next satellite index in the same orbit
                destIndex = destOrbitId * sat_per_orbit + destIndexInOrbit  # next satellite id
                # create the intra-orbit-isl
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                isl_band_width,
                                                                InterSatelliteLink.InterSatelliteLink.LinkType.INTRA_ORBIT)
                self.satellites[sourceIndex].interfaceIndex += 1
                self.satellites[destIndex].interfaceIndex += 1
                self.ISLs.append(linkTmp)
                # create the inter-orbit-isl
                destOrbitId = sourceOrbitId + 1
                # same index in the next orbit
                destIndexInOrbit = sourceIndexInOrbit
                if destOrbitId < orbit_number:
                    destIndex = destOrbitId * sat_per_orbit + destIndexInOrbit
                    linkId = len(self.ISLs)
                    linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                    self.satellites[sourceIndex].interfaceIndex,
                                                                    self.satellites[destIndex],
                                                                    self.satellites[destIndex].interfaceIndex,
                                                                    isl_band_width,
                                                                    InterSatelliteLink.InterSatelliteLink.LinkType.
                                                                    INTER_ORBIT)
                    self.satellites[sourceIndex].interfaceIndex += 1
                    self.satellites[destIndex].interfaceIndex += 1
                    self.ISLs.append(linkTmp)

            # calculate the inter-orbit links among the first and last orbit ISLs
            for sourceIndex in range(0, sat_per_orbit):
                destIndex = (orbit_number - 1) * sat_per_orbit + sourceIndex
                linkId = len(self.ISLs)
                linkTmp = InterSatelliteLink.InterSatelliteLink(linkId, self.satellites[sourceIndex],
                                                                self.satellites[sourceIndex].interfaceIndex,
                                                                self.satellites[destIndex],
                                                                self.satellites[destIndex].interfaceIndex,
                                                                isl_band_width,
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

    @classmethod
    def getPreviousSatelliteIndex(cls, satellite_id, sat_per_orbit):
        satellite_per_orbit = sat_per_orbit
        orbit_id = int(satellite_id / satellite_per_orbit)
        return (satellite_id + satellite_per_orbit - 1) % satellite_per_orbit + orbit_id * satellite_per_orbit

    @classmethod
    def getNextSatelliteIndex(cls, satellite_id, sat_per_orbit):
        satellite_per_orbit = sat_per_orbit
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
        sat_per_orbit = self.config_reader.sat_per_orbit
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
            source_previous_id = Constellation.getPreviousSatelliteIndex(source_sat_id, sat_per_orbit)
            dest_previous_id = Constellation.getPreviousSatelliteIndex(dest_sat_id, sat_per_orbit)
            # get source and dest next satellite
            source_next_id = Constellation.getNextSatelliteIndex(source_sat_id, sat_per_orbit)
            dest_next_id = Constellation.getNextSatelliteIndex(dest_sat_id, sat_per_orbit)
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
        finalStr += "orbitNumber: " + str(self.config_reader.orbit_number) + "\n"
        finalStr += "satPerOrbit: " + str(self.config_reader.sat_per_orbit) + "\n"
        finalStr += "inclination: " + str(self.config_reader.inclination) + "\n"
        finalStr += "startingPhase: " + str(self.config_reader.starting_phase) + "\n"
        finalStr += "altitude: " + str(self.config_reader.altitude) + "\n"
        finalStr += "routingProtocol: " + str(self.config_reader.routing_protocol) + "\n"
        finalStr += "satellites: " + "\n"
        for satellite in self.satellites:
            finalStr += str(satellite) + "\n"
        finalStr += "ISLs: " + "\n"
        for isl in self.ISLs:
            finalStr += str(isl) + "\n"
        return finalStr
