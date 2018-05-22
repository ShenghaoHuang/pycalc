class Person:
    def __init__(self):
        self._age = 18
        self._name = "Mike"

    @property
    def name(self):
        return self._name

    def age(self):
        return self._age


π = 3.14


def multpi(mult):
    return mult*π