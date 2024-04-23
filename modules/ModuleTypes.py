from enum import Enum


class ConstellationType(Enum):
    """
    constellation types
    """
    WALKER_STAR = 1
    WALKER_DELTA = 2

    def __str__(self):
        return str(self.name)

    @classmethod
    def convert_str_to_constellation_type(cls, constellation_type_str):
        if constellation_type_str == "WALKER_STAR":
            return ConstellationType.WALKER_STAR
        elif constellation_type_str == "WALKER_DELTA":
            return ConstellationType.WALKER_DELTA
        else:
            raise ValueError("Unknown constellation type: " + constellation_type_str)


class RoutingProtocols(Enum):
    """
    routing protocols
    """
    NONE = 0,
    IP_OSPF = 1,
    LIPSIN = 2,

    def __str__(self):
        return str(self.name)

    @classmethod
    def convert_str_to_routing_protocol(cls, routing_protocol_str):
        if routing_protocol_str == "None":
            return RoutingProtocols.NONE
        elif routing_protocol_str == "IP_OSPF":
            return RoutingProtocols.IP_OSPF
        elif routing_protocol_str == "LIPSIN":
            return RoutingProtocols.LIPSIN
        else:
            raise ValueError("Unknown routing protocol: " + routing_protocol_str)
