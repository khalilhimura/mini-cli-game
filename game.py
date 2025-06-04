import json
import os # For checking file existence
import random # For event triggering
from colony import Colony
from buildings import Mine, SolarPanel, HydroponicsFarm, ResearchLab, GeothermalPlant # Added GeothermalPlant
from events import Event, MinorResourceBoost, SmallResourceDrain, ProductionSpike, MeteorStrikeWarning

# Base per-second production rates
BASE_MINERALS_PER_SECOND = 1.0
BASE_ENERGY_PER_SECOND = 1.0
BASE_FOOD_PER_SECOND = 0.2
BASE_RESEARCH_PER_SECOND = 0.0

# Mapping of building identifier strings (as stored in save files)
# to their corresponding classes for reconstruction.
BUILDING_CLASSES = {
    "Mine": Mine,
    "Solar Panel": SolarPanel,
    "Hydroponics Farm": HydroponicsFarm,
    "Research Lab": ResearchLab,
    "Geothermal Plant": GeothermalPlant,
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

# Old generate_resources function (turn-based) is being replaced by the time-based one below
# def generate_resources(colony_instance):
#     """
#     Generates resources for the colony, including base production and building bonuses.
#     """
#     # Base production
#     base_production = {"Minerals": 1, "Energy": 1} # Adjusted base production for clarity
#
#     # Get production bonuses from buildings
#     building_bonuses = colony_instance.calculate_production_bonuses()
#
#     # Calculate total production for each resource
#     total_production = {}
#     all_resource_types = set(base_production.keys()) | set(building_bonuses.keys())
#
#     for resource_name in all_resource_types:
#         base = base_production.get(resource_name, 0)
#         bonus = building_bonuses.get(resource_name, 0)
#         total_production[resource_name] = base + bonus
#         # print(f"Generating {resource_name}: Base={base}, Bonus={bonus}, Total={base+bonus}")
#
#
#     # Add resources to the colony
#     for resource_name, amount in total_production.items():
#         if amount > 0: # Only add if there's something to add
#             colony_instance.add_resource(resource_name, amount)


def generate_resources(colony_instance, time_delta_seconds):
    """
    Generates resources for the colony based on time passed, base rates, and building bonuses.
    Bonuses are now interpreted as 'per second'.
    """
    building_bonuses = colony_instance.calculate_production_bonuses()

    # Define base rates for all relevant resources
    base_rates = {
        "Minerals": BASE_MINERALS_PER_SECOND,
        "Energy": BASE_ENERGY_PER_SECOND,
        "Food": BASE_FOOD_PER_SECOND,
        "ResearchPoints": BASE_RESEARCH_PER_SECOND
    }

    # Get all unique resource types from base rates and bonuses
    # Ensure all resources defined in base_rates are considered, even if no building produces them yet.
    all_resource_names = set(base_rates.keys()) | set(building_bonuses.keys())

    for resource_name in all_resource_names:
        base_rate = base_rates.get(resource_name, 0.0)
        # Ensure bonus_rate is 0.0 if resource_name not in building_bonuses (e.g. for Food/Research initially)
        bonus_rate = building_bonuses.get(resource_name, 0.0) 
        
        total_rate = base_rate + bonus_rate
        amount_to_add = total_rate * time_delta_seconds
        
        if amount_to_add > 0 or (resource_name in colony_instance.resources and colony_instance.resources[resource_name] > 0) :
            # Add resource if it's being produced, or ensure it exists in colony.resources if it has a base rate
            # The check for existing resources and positive amount is to ensure that even if a resource has 0 production,
            # it's handled correctly by add_resource if it was already present (e.g. initial Food)
            # The primary condition is `amount_to_add > 0`.
            # The current add_resource in colony.py handles adding new resource types if they appear.
            if amount_to_add != 0: # Avoid adding 0.0 constantly if no production and no initial amount
                 colony_instance.add_resource(resource_name, amount_to_add)

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
        # print(f"Error: Save file '{filename}' not found.") # CLI print, might not be desired in curses
        return None

    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        # Create a new Colony instance, now passing the turn number
        loaded_turn_number = data.get("turn_number", 1) # Default to 1 if not found
        new_colony = Colony(initial_turn_number=loaded_turn_number) # This will set default resources
        
        # Overwrite with saved resources, ensuring all types are handled and default if missing
        saved_resources = data.get("resources", {})
        new_colony.resources["Minerals"] = float(saved_resources.get("Minerals", 0.0))
        new_colony.resources["Energy"] = float(saved_resources.get("Energy", 0.0))
        new_colony.resources["Food"] = float(saved_resources.get("Food", 0.0))
        new_colony.resources["ResearchPoints"] = float(saved_resources.get("ResearchPoints", 0.0))
        
        # Reconstruct buildings
        buildings_data = data.get("buildings", []) # Expects a list of dicts
        for building_data in buildings_data:
            if isinstance(building_data, dict): # New format: {"name": "Mine", "level": 1}
                name = building_data.get("name")
                level = building_data.get("level", 1)
            else: # Old format: "Mine" (string) - for backward compatibility if needed
                name = building_data 
                level = 1 # Default level for old save format

            building_class = BUILDING_CLASSES.get(name)
            if not building_class:
                # Support loading buildings saved with display names that don't
                # match the dictionary keys (e.g. "Geothermal Plant" vs
                # "GeothermalPlant").
                normalized_name = name.replace(" ", "") if isinstance(name, str) else name
                building_class = BUILDING_CLASSES.get(normalized_name)

            if building_class:
                building_instance = building_class()
                building_instance.level = level  # Set the loaded level
                new_colony.add_building(building_instance)
            else:
                # Silently skip unknown building types. In a full game we might
                # want to log this for debugging.
                pass
        
        # Load research data
        new_colony.completed_research = set(data.get("completed_research", []))
        # Default for unlocked_buildings should match Colony.__init__ if key is missing
        default_unlocked_buildings = {"Mine", "Solar Panel", "Hydroponics Farm", "Research Lab"}
        new_colony.unlocked_buildings = set(data.get("unlocked_buildings", list(default_unlocked_buildings)))
        
        # Load event history
        new_colony.event_history = data.get("event_history", [])


        # print(f"Game loaded successfully from {filename}.") # CLI
        return new_colony
    except IOError as e:
        print(f"Error loading game (IOError): {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error loading game (JSONDecodeError): {e}. Save file might be corrupted.")
        return None
    except Exception as e: # Catch any other potential errors during reconstruction
        # print(f"An unexpected error occurred while loading the game: {e}") # CLI print
        return None

AVAILABLE_EVENT_CLASSES = [MinorResourceBoost, SmallResourceDrain, ProductionSpike, MeteorStrikeWarning]

def trigger_random_event(colony_instance, available_event_classes):
    """
    Attempts to trigger a random event based on a chance.
    If an event is triggered, it's applied to the colony and its message is logged.
    """
    if not available_event_classes:
        return None # No event classes defined to trigger

    # Example: 10% chance to trigger an event per call
    # This chance mechanism might be tied to the event_trigger_interval in main.py
    # i.e., this function is called every interval, and then there's a chance within that.
    
    # Self-correction: Adjusting event trigger chance for testing major events more easily
    # For actual gameplay, this might be lower or vary per event type
    if random.random() < 0.15: # Adjusted chance to 15%
        # Randomly select an event *class*
        SelectedEventClass = random.choice(available_event_classes)
        
        # Instantiate the selected event class
        event_instance = SelectedEventClass() # Event-specific __init__ is called here

        if event_instance.is_major:
            return event_instance # Return the event instance itself for major events
        else:
            # For background events, apply immediately and add to history
            message = event_instance.apply(colony_instance) # Pass None for choice_key
            colony_instance.add_event_to_history(message)
            return None # Indicate no major event popup needed
    
    return None # No event triggered

def resolve_major_event(colony, event_instance, choice_key):
    if not event_instance or not event_instance.is_major:
        return
    outcome_message = event_instance.apply(colony, choice_key)
    colony.add_event_to_history(outcome_message)
