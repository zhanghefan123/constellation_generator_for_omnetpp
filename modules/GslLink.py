from enum import Enum


def convert_str_to_bandwidth(bandwidth_str):
    """
    convert string to bandwidth
    :param bandwidth_str:  string of bandwidth
    :return:
    """
    if bandwidth_str == "10 Mbps":
        return GslLink.BandWidth.SatToGround_10Mbps
    elif bandwidth_str == "100 Mbps":
        return GslLink.BandWidth.SatToGround_100Mbps
    elif bandwidth_str == "1000 Mbps":
        return GslLink.BandWidth.SatToGround_1Gbps
    else:
        return None


class GslLink:
    class BandWidth(Enum):
        """
        bandwidth of the link
        """
        SatToGround_10Mbps = 10,
        SatToGround_100Mbps = 100,
        SatToGround_1Gbps = 1000

        def __str__(self):
            return str(self.name)
