class Building:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

class Mine(Building):
    def __init__(self):
        super().__init__(name="Mine", cost={"Minerals": 50})
        self.production_bonus = {"Minerals": 5}

class SolarPanel(Building):
    def __init__(self):
        super().__init__(name="Solar Panel", cost={"Minerals": 30, "Energy": 20})
        self.production_bonus = {"Energy": 3}
