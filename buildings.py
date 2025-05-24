class Building:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.level = 1

    def upgrade_cost(self):
        return {"Minerals": 99999, "Energy": 99999}

    def get_production_bonus(self):
        return {}

class Mine(Building):
    def __init__(self):
        super().__init__(name="Mine", cost={"Minerals": 50})

    def upgrade_cost(self):
        return {
            "Minerals": int(25 * (self.level**1.5)),
            "Energy": int(10 * (self.level**1.5)),
        }

    def get_production_bonus(self):
        return {"Minerals": 5 * self.level}

class SolarPanel(Building):
    def __init__(self):
        super().__init__(name="Solar Panel", cost={"Minerals": 30, "Energy": 20})

    def upgrade_cost(self):
        return {
            "Minerals": int(15 * (self.level**1.5)),
            "Energy": int(10 * (self.level**1.5)),
        }

    def get_production_bonus(self):
        return {"Energy": 3 * self.level}

class HydroponicsFarm(Building):
    def __init__(self):
        super().__init__(name="Hydroponics Farm", cost={"Minerals": 70.0, "Energy": 30.0})

    def upgrade_cost(self):
        return {
            "Minerals": int(35 * (self.level**1.5)),
            "Energy": int(20 * (self.level**1.5)),
        }

    def get_production_bonus(self):
        return {"Food": 2.0 * self.level}

class ResearchLab(Building):
    def __init__(self):
        super().__init__(name="Research Lab", cost={"Minerals": 100.0, "Energy": 50.0})

    def upgrade_cost(self):
        return {
            "Minerals": int(50 * (self.level**1.5)),
            "Energy": int(25 * (self.level**1.5)),
        }

    def get_production_bonus(self):
        return {"ResearchPoints": 0.5 * self.level}

class GeothermalPlant(Building):
    def __init__(self):
        super().__init__(name="Geothermal Plant", cost={"Minerals": 150, "Energy": 100})
        # self.level is initialized in the base Building class

    def upgrade_cost(self):
        base_minerals = 75
        base_energy = 50
        return {
            "Minerals": int(base_minerals * (self.level**1.5)),
            "Energy": int(base_energy * (self.level**1.5)),
        }

    def get_production_bonus(self):
        base_energy_bonus = 10
        return {"Energy": base_energy_bonus * self.level}
