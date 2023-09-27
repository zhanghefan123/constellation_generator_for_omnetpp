from enum import Enum


def convert_str_to_bandwidth(bandwidth_str):
    """
    convert string to bandwidth
    :param bandwidth_str:  string of bandwidth
    :return:
    """
    if bandwidth_str == "10 Mbps":
        return InterSatelliteLink.BandWidth.SatToSat_10Mbps
    elif bandwidth_str == "100 Mbps":
        return InterSatelliteLink.BandWidth.SatToSat_100Mbps
    elif bandwidth_str == "1000 Mbps":
        return InterSatelliteLink.BandWidth.SatToSat_1Gbps
    else:
        return None


class InterSatelliteLink:
    class LinkType(Enum):
        """
        Link type of inter satellite link
        """
        INTRA_ORBIT = 1,
        INTER_ORBIT = 2,

        def __str__(self):
            if self.name == "INTRA_ORBIT":
                return "intra-orbit"
            elif self.name == "INTER_ORBIT":
                return "inter-orbit"

    class BandWidth(Enum):
        """
        bandwidth of the link
        """
        SatToSat_10Mbps = 10,
        SatToSat_100Mbps = 100,
        SatToSat_1Gbps = 1000

        def __str__(self):
            return str(self.name)

    def __init__(self, linkId, sourceSatellite, sourceInterfaceIndex,
                 destinationSatellite, destInterfaceIndex, bandWidth, linkType):
        """
        initialize the link object
        :param linkId:  link id
        :param sourceSatellite:  source satellite
        :param sourceInterfaceIndex:  source interface index
        :param destinationSatellite:  destination satellite
        :param destInterfaceIndex: destination interface index
        :param bandWidth:  bandwidth
        :param linkType:  link type
        """
        self.linkId = linkId
        self.sourceSatellite = sourceSatellite
        self.sourceInterfaceIndex = sourceInterfaceIndex
        self.destinationSatellite = destinationSatellite
        self.destInterfaceIndex = destInterfaceIndex
        self.bandWidth = bandWidth
        self.linkType = linkType

    def __str__(self):
        """string in single line"""
        return (str(self.linkId) + " " +
                "satellite" + str(self.sourceSatellite.satellite_id) + " " +
                "ethg[" + str(self.sourceInterfaceIndex) + "]" +
                " --> " +
                "satellite" + str(self.destinationSatellite.satellite_id) + " " +
                "ethg[" + str(self.destInterfaceIndex) + "]" + " " +
                str(self.bandWidth) + " " + str(self.linkType))
