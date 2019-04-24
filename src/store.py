from abc import ABC


class Store(ABC):
    """ Abstract base class for an item sold by the grocery store."""

    def __init__(self, name, location):
        self.name = name 
        self.location = location

    def get_name(self):
        return self.name

    def get_loc(self):
        return self.location

