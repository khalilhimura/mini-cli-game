from collections import defaultdict

class Colony:
    def __init__(self, initial_turn_number=1):
        self.resources = {"Minerals": 0, "Energy": 0}
        self.buildings = []
        self.turn_number = initial_turn_number

    def get_resources(self):
        return self.resources

    def add_resource(self, resource_name, amount):
        if resource_name in self.resources:
            self.resources[resource_name] += amount
        else:
            # Or handle this as an error, e.g., raise ValueError
            print(f"Warning: Resource '{resource_name}' not found. Adding it to resources.")
            self.resources[resource_name] = amount

    def add_building(self, building_instance):
        self.buildings.append(building_instance)

    def get_buildings(self):
        return self.buildings

    def has_enough_resources(self, cost_dict):
        for resource_name, required_amount in cost_dict.items():
            if self.resources.get(resource_name, 0) < required_amount:
                return False
        return True

    def spend_resources(self, cost_dict):
        if self.has_enough_resources(cost_dict):
            for resource_name, cost_amount in cost_dict.items():
                self.resources[resource_name] -= cost_amount
            return True
        return False

    def calculate_production_bonuses(self):
        bonuses = defaultdict(int)
        for building in self.buildings:
            if hasattr(building, 'production_bonus'):
                for resource_name, bonus_amount in building.production_bonus.items():
                    bonuses[resource_name] += bonus_amount
        return dict(bonuses)

    def to_dict(self):
        return {
            "resources": self.resources,
            "buildings": [building.name for building in self.buildings],
            "turn_number": self.turn_number
        }
