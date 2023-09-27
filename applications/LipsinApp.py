class LipsinApp:
    def __init__(self, source, destinations):
        """
        initialize the lipsin app
        :param source:  the source satellite id
        :param destinations:  the destination satellite ids
        """
        self.source = source
        self.destinations = destinations

    def __str__(self):
        return "LipsinApp: source: " + str(self.source) + ", destinations: " + str(self.destinations)
