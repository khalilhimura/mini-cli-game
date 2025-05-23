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
        self.production_bonus = {"Energy": 3} # Interpreted as per second by game.py

class HydroponicsFarm(Building):
    def __init__(self):
        super().__init__(name="Hydroponics Farm", cost={"Minerals": 70.0, "Energy": 30.0})
        self.production_bonus = {"Food": 2.0} # Food per second

class ResearchLab(Building):
    def __init__(self):
        super().__init__(name="Research Lab", cost={"Minerals": 100.0, "Energy": 50.0})
        self.production_bonus = {"ResearchPoints": 0.5} # Research Points per second
