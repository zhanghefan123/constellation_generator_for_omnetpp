from enum import Enum


class LipsinLinkType(Enum):
    PHYSICAL_LINK = 1,
    VIRTUAL_LINK = 2,


class LipsinLink:
    def __init__(self, linkId, lipsinLinkType, sourceInterfaceIndex,
                 sourceSatelliteId, destinationSatelliteId, linkCost, linkType):
        self.linkId = linkId
        self.lipsinLinkType = lipsinLinkType
        self.sourceInterfaceIndex = sourceInterfaceIndex
        self.sourceSatelliteId = sourceSatelliteId
        self.destinationSatelliteId = destinationSatelliteId
        self.linkCost = linkCost
        self.linkType = linkType
