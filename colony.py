from collections import defaultdict

class Colony:
    def __init__(self, initial_turn_number=1):
        # Adjusted initial values for testing; Minerals & Energy also adjusted for consistency
        self.resources = {
            "Minerals": 50.0, 
            "Energy": 60.0, 
            "Food": 10.0, 
            "ResearchPoints": 0.0
        }
        self.buildings = []
        self.turn_number = initial_turn_number
        self.event_history = []

    def get_resources(self):
        return self.resources

    def add_resource(self, resource_name, amount):
        if resource_name in self.resources:
            self.resources[resource_name] += float(amount) # Ensure amount is float
        else:
            # Or handle this as an error, e.g., raise ValueError
            print(f"Warning: Resource '{resource_name}' not found. Adding it to resources.")
            self.resources[resource_name] = float(amount) # Ensure amount is float

    def add_building(self, building_instance):
        self.buildings.append(building_instance)

    def get_buildings(self):
        return self.buildings

    def has_enough_resources(self, cost_dict):
        for resource_name, required_amount in cost_dict.items():
            if self.resources.get(resource_name, 0.0) < float(required_amount): # Compare with float
                return False
        return True

    def spend_resources(self, cost_dict):
        if self.has_enough_resources(cost_dict):
            for resource_name, cost_amount in cost_dict.items():
                self.resources[resource_name] -= float(cost_amount) # Ensure amount is float
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

    def add_event_to_history(self, event_message, max_history=10):
        self.event_history.insert(0, event_message) # Add to the beginning
        self.event_history = self.event_history[:max_history] # Keep only the last max_history items
