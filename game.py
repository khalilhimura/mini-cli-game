import json
import os # For checking file existence
from colony import Colony
from buildings import Mine, SolarPanel # Assuming these are the building classes

# Mapping building names to their classes for reconstruction
BUILDING_CLASSES = {
    "Mine": Mine,
    "Solar Panel": SolarPanel
    # Add other building classes here if you create more
}

def build_structure(colony_instance, building_class):
    """
    Attempts to build a structure for the colony.

    Args:
        colony_instance: An instance of the Colony class.
        building_class: The class of the building to be built (e.g., Mine, SolarPanel).

    Returns:
        True if building was successful, False otherwise.
    """
    # Create a temporary instance to get its cost and name
    # This is because cost is defined on the instance in the current setup
    temp_building = building_class()
    cost = temp_building.cost
    # building_name = temp_building.name # Not used in this function currently

    if colony_instance.has_enough_resources(cost):
        if colony_instance.spend_resources(cost):
            # Create the actual building instance to be added to the colony
            new_building = building_class()
            colony_instance.add_building(new_building)
            print(f"Successfully built {new_building.name}.")
            return True
        else:
            # Should not happen if has_enough_resources was True
            print("Error: Spending resources failed even after check.")
            return False
    else:
        print(f"Not enough resources to build {temp_building.name}.")
        missing_resources = []
        for resource, required_amount in cost.items():
            current_amount = colony_instance.resources.get(resource, 0)
            if current_amount < required_amount:
                missing_resources.append(f"{required_amount - current_amount} {resource}")
        print(f"Missing: {', '.join(missing_resources)}")
        return False

def generate_resources(colony_instance):
    """
    Generates resources for the colony, including base production and building bonuses.
    """
    # Base production
    base_production = {"Minerals": 1, "Energy": 1} # Adjusted base production for clarity

    # Get production bonuses from buildings
    building_bonuses = colony_instance.calculate_production_bonuses()

    # Calculate total production for each resource
    total_production = {}
    all_resource_types = set(base_production.keys()) | set(building_bonuses.keys())

    for resource_name in all_resource_types:
        base = base_production.get(resource_name, 0)
        bonus = building_bonuses.get(resource_name, 0)
        total_production[resource_name] = base + bonus
        # print(f"Generating {resource_name}: Base={base}, Bonus={bonus}, Total={base+bonus}")


    # Add resources to the colony
    for resource_name, amount in total_production.items():
        if amount > 0: # Only add if there's something to add
            colony_instance.add_resource(resource_name, amount)
    # print(f"Resources after generation: {colony_instance.get_resources()}")


def save_game(colony_instance, filename="savegame.json"):
    """
    Saves the current state of the colony to a JSON file.
    """
    game_state = colony_instance.to_dict()
    try:
        with open(filename, 'w') as f:
            json.dump(game_state, f, indent=4)
        print(f"Game saved successfully to {filename}.")
    except IOError as e:
        print(f"Error saving game: {e}")

def load_game(filename="savegame.json"):
    """
    Loads the game state from a JSON file.
    Returns a Colony instance or None if loading fails.
    """
    if not os.path.exists(filename):
        print(f"Error: Save file '{filename}' not found.")
        return None

    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        # Create a new Colony instance, now passing the turn number
        loaded_turn_number = data.get("turn_number", 1) # Default to 1 if not found
        new_colony = Colony(initial_turn_number=loaded_turn_number)
        
        new_colony.resources = data.get("resources", {"Minerals": 0, "Energy": 0})
        
        # Reconstruct buildings
        building_names = data.get("buildings", [])
        for name in building_names:
            building_class = BUILDING_CLASSES.get(name)
            if building_class:
                # Create a new instance of the building
                building_instance = building_class() 
                new_colony.add_building(building_instance) # Use add_building for consistency
            else:
                print(f"Warning: Building class for '{name}' not found. Skipping.")
        
        print(f"Game loaded successfully from {filename}.")
        return new_colony
    except IOError as e:
        print(f"Error loading game (IOError): {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error loading game (JSONDecodeError): {e}. Save file might be corrupted.")
        return None
    except Exception as e: # Catch any other potential errors during reconstruction
        print(f"An unexpected error occurred while loading the game: {e}")
        return None
