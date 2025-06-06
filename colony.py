from collections import defaultdict
import random
from research import RESEARCH_PROJECTS # Import RESEARCH_PROJECTS

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
        self.completed_research = set()
        self.unlocked_buildings = {"Mine", "Solar Panel", "Hydroponics Farm", "Research Lab"}

    def research_project(self, project_id):
        if project_id not in RESEARCH_PROJECTS:
            self.add_event_to_history(f"Error: Research project '{project_id}' not found.")
            return False

        if project_id in self.completed_research:
            self.add_event_to_history(f"Project '{RESEARCH_PROJECTS[project_id]['name']}' already researched.")
            return False

        project_details = RESEARCH_PROJECTS[project_id]
        cost = project_details["cost"]

        if self.resources.get("ResearchPoints", 0.0) >= cost:
            self.resources["ResearchPoints"] -= cost
            self.completed_research.add(project_id)

            for building_name in project_details.get("unlocks_buildings", []):
                self.unlocked_buildings.add(building_name)
            
            # Future: Handle unlocks_upgrades
            
            self.add_event_to_history(
                f"Research complete: {project_details['name']}. Unlocked: {', '.join(project_details.get('unlocks_buildings', [])) or 'None'}."
            )
            return True
        else:
            self.add_event_to_history(
                f"Not enough Research Points for '{project_details['name']}'. Need {cost}, have {self.resources.get('ResearchPoints', 0.0):.0f}."
            )
            return False

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

    def damage_random_building(self):
        """Randomly damages one of the colony's buildings.
        If the selected building is level 1 it is destroyed.
        Returns a short description of the damage.
        """
        if not self.buildings:
            return "No buildings to damage."

        building = random.choice(self.buildings)
        if building.level > 1:
            building.level -= 1
            return f"{building.name} damaged and downgraded to level {building.level}."
        else:
            self.buildings.remove(building)
            return f"{building.name} destroyed."

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
        bonuses = defaultdict(float) # Changed to float to handle potential float bonuses
        for building in self.buildings:
            # All building instances should have get_production_bonus method
            # from the base Building class, so no need for hasattr check if
            # all building objects are instantiated correctly.
            for resource_name, bonus_amount in building.get_production_bonus().items():
                bonuses[resource_name] += bonus_amount
        return dict(bonuses)

    def upgrade_building(self, building_instance_index):
        if (
            building_instance_index < 0
            or building_instance_index >= len(self.buildings)
        ):
            self.add_event_to_history("Error: Invalid building index for upgrade.")
            return False
        building_to_upgrade = self.buildings[building_instance_index]

        current_upgrade_cost = building_to_upgrade.upgrade_cost()

        if self.has_enough_resources(current_upgrade_cost):
            self.spend_resources(current_upgrade_cost)
            building_to_upgrade.level += 1
            self.add_event_to_history(
                f"{building_to_upgrade.name} upgraded to level {building_to_upgrade.level}."
            )
            return True
        else:
            self.add_event_to_history(
                f"Not enough resources to upgrade {building_to_upgrade.name} to level {building_to_upgrade.level + 1}."
            )
            return False

    def to_dict(self):
        return {
            "resources": self.resources,
            "buildings": [{"name": building.name, "level": building.level} for building in self.buildings],
            "turn_number": self.turn_number,
            "event_history": self.event_history, # Ensure event_history is saved
            "completed_research": list(self.completed_research),
            "unlocked_buildings": list(self.unlocked_buildings)
        }

    def add_event_to_history(self, event_message, max_history=10):
        self.event_history.insert(0, event_message) # Add to the beginning
        self.event_history = self.event_history[:max_history] # Keep only the last max_history items
