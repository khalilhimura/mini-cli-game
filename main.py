from colony import Colony
from game import generate_resources, build_structure, save_game, load_game
from buildings import Mine, SolarPanel
import os # For checking save file existence before loading, if desired outside load_game

def main():
    # Initialization
    my_colony = Colony(initial_turn_number=1) # Colony now manages its own turn number
    
    # Initial Resources
    print("Booting up colony systems...")
    # Check for a save file to offer loading first
    if os.path.exists("savegame.json"):
        load_choice = input("Save game found. Load it? (y/n): ").strip().lower()
        if load_choice == 'y':
            loaded_data = load_game("savegame.json")
            if loaded_data:
                my_colony = loaded_data
                print("Game loaded.")
            else:
                print("Failed to load game. Starting a new game.")
                my_colony.add_resource("Minerals", 100) 
                my_colony.add_resource("Energy", 50)
        else:
            print("Starting a new game.")
            my_colony.add_resource("Minerals", 100) 
            my_colony.add_resource("Energy", 50)
    else:
        print("No save game found. Starting a new game.")
        my_colony.add_resource("Minerals", 100) 
        my_colony.add_resource("Energy", 50)
    
    print("Initial resources set/loaded.")
    print("-" * 30)

    # Game Loop
    while True:
        # Synchronize main.py's turn_number display with the colony's turn_number
        # The colony's turn_number is the source of truth after loading.
        turn_number_display = my_colony.turn_number 
        print(f"\n--- Turn {turn_number_display} ---")

        # Display Status
        print("Colony Status:")
        current_resources = my_colony.get_resources()
        print(f"  Resources: Minerals - {current_resources.get('Minerals', 0)}, Energy - {current_resources.get('Energy', 0)}")

        current_buildings = my_colony.get_buildings()
        if not current_buildings:
            print("  Buildings: None")
        else:
            building_names = [building.name for building in current_buildings]
            print(f"  Buildings: {', '.join(building_names)}")
        
        bonuses = my_colony.calculate_production_bonuses()
        base_prod_min = 1 
        base_prod_energy = 1
        print(f"  Expected next turn generation (base + bonus): Minerals +{bonuses.get('Minerals', 0) + base_prod_min}, Energy +{bonuses.get('Energy', 0) + base_prod_energy}")
        print("-" * 30)

        # Display Options
        print("Available Actions:")
        mine_cost = Mine().cost
        solar_panel_cost = SolarPanel().cost
        print(f"  1. Build Mine (Cost: {mine_cost['Minerals']} Minerals)")
        print(f"  2. Build Solar Panel (Cost: {solar_panel_cost['Minerals']} Minerals, {solar_panel_cost['Energy']} Energy)")
        print("  3. Wait (Generate resources and go to Next Turn)")
        print("  4. Save Game")
        print("  5. Load Game")
        print("  6. Exit Game")
        print("-" * 30)

        # Get Player Input
        choice = input("Enter your choice (1-6): ")
        print("-" * 30) 

        # Process Input
        progress_turn = False
        if choice == "1":
            build_structure(my_colony, Mine) 
            progress_turn = True
        elif choice == "2":
            build_structure(my_colony, SolarPanel)
            progress_turn = True
        elif choice == "3":
            generate_resources(my_colony)
            print("Resources generated for the turn.")
            progress_turn = True
        elif choice == "4": # Save Game
            save_game(my_colony)
            # Turn does not progress after saving
        elif choice == "5": # Load Game
            loaded_colony_data = load_game() # Uses default "savegame.json"
            if loaded_colony_data:
                my_colony = loaded_colony_data
                # turn_number_display is updated at the start of the loop from my_colony.turn_number
                print("Game state loaded.")
            else:
                print("Failed to load game. Continuing with current game state.")
            # Turn does not progress after attempting to load
        elif choice == "6": # Exit
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        if progress_turn:
            my_colony.turn_number += 1 # Increment the turn number in the colony object
        
        print("-" * 30)

if __name__ == "__main__":
    main()
