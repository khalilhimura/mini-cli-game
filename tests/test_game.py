import unittest
import sys
import os
import json

sys.path.append('..') # Add the project root to the Python path

from colony import Colony
from buildings import Mine, SolarPanel
from game import generate_resources, build_structure, save_game, load_game, BUILDING_CLASSES

class TestGame(unittest.TestCase):
    def setUp(self):
        """Create a fresh Colony instance and define save filename before each test."""
        self.colony = Colony(initial_turn_number=1)
        self.save_filename = "test_savegame.json"

    def tearDown(self):
        """Remove the test save file if it exists after each test."""
        if os.path.exists(self.save_filename):
            os.remove(self.save_filename)

    def test_generate_resources_base(self):
        """Test base resource generation without any buildings."""
        # Assuming base production is 1 Mineral and 1 Energy as per game.py logic
        generate_resources(self.colony)
        resources = self.colony.get_resources()
        self.assertEqual(resources.get("Minerals", 0), 1)
        self.assertEqual(resources.get("Energy", 0), 1)

    def test_generate_resources_with_bonus(self):
        """Test resource generation with building bonuses."""
        self.colony.add_building(Mine()) # Mine produces 5 Minerals
        # Base production: 1 Mineral, 1 Energy
        # Mine bonus: 5 Minerals
        # Expected: 1+5 = 6 Minerals, 1 Energy
        generate_resources(self.colony)
        resources = self.colony.get_resources()
        self.assertEqual(resources.get("Minerals", 0), 6) # 1 (base) + 5 (mine)
        self.assertEqual(resources.get("Energy", 0), 1)   # 1 (base)

        self.colony.add_building(SolarPanel()) # SolarPanel produces 3 Energy
        # Previous state: 6 Minerals, 1 Energy. Buildings: Mine, SolarPanel
        # New generation:
        # Base: 1 Mineral, 1 Energy
        # Mine: +5 Minerals
        # SolarPanel: +3 Energy
        # Total new: 6 Minerals, 4 Energy
        # Expected after this generation: 6+6=12 Minerals, 1+4=5 Energy
        generate_resources(self.colony)
        resources = self.colony.get_resources()
        self.assertEqual(resources.get("Minerals", 0), 12) # 6 (previous) + 1 (base) + 5 (mine)
        self.assertEqual(resources.get("Energy", 0), 5)   # 1 (previous) + 1 (base) + 3 (solar)


    def test_build_structure_success(self):
        """Test building a structure with sufficient resources."""
        self.colony.add_resource("Minerals", Mine().cost["Minerals"]) # Give exactly enough Minerals
        
        # Capture output for build_structure (optional, but good for checking messages)
        # For now, just test functionality
        initial_minerals = self.colony.get_resources()["Minerals"]
        
        build_success = build_structure(self.colony, Mine)
        self.assertTrue(build_success) # build_structure should indicate success
        
        self.assertEqual(len(self.colony.get_buildings()), 1)
        self.assertIsInstance(self.colony.get_buildings()[0], Mine)
        # Check if resources were deducted correctly
        self.assertEqual(self.colony.get_resources()["Minerals"], initial_minerals - Mine().cost["Minerals"])

    def test_build_structure_insufficient_resources(self):
        """Test building a structure with insufficient resources."""
        initial_minerals = 10
        self.colony.add_resource("Minerals", initial_minerals) # Not enough for a Mine (cost 50)
        
        build_success = build_structure(self.colony, Mine)
        self.assertFalse(build_success) # build_structure should indicate failure or return False
        
        self.assertEqual(len(self.colony.get_buildings()), 0)
        self.assertEqual(self.colony.get_resources()["Minerals"], initial_minerals) # Resources unchanged

    def test_save_and_load_game(self):
        """Test saving and loading the game state."""
        # Setup initial state
        self.colony.add_resource("Minerals", 250)
        self.colony.add_resource("Energy", 150)
        self.colony.add_building(Mine())
        self.colony.add_building(SolarPanel())
        self.colony.turn_number = 5

        original_resources = self.colony.get_resources().copy()
        original_building_names = [b.name for b in self.colony.get_buildings()]
        original_turn_number = self.colony.turn_number

        # Save the game
        save_game(self.colony, self.save_filename)
        self.assertTrue(os.path.exists(self.save_filename))

        # Load the game
        loaded_colony = load_game(self.save_filename)
        self.assertIsNotNone(loaded_colony)

        # Compare loaded state with original state
        self.assertEqual(loaded_colony.get_resources(), original_resources)
        
        loaded_building_names = [b.name for b in loaded_colony.get_buildings()]
        self.assertEqual(len(loaded_building_names), len(original_building_names))
        self.assertListEqual(sorted(loaded_building_names), sorted(original_building_names)) # Order might change

        self.assertEqual(loaded_colony.turn_number, original_turn_number)

    def test_load_game_file_not_found(self):
        """Test loading a game when the save file does not exist."""
        loaded_colony = load_game("non_existent_savefile.json")
        self.assertIsNone(loaded_colony)

    def test_load_game_corrupted_json(self):
        """Test loading a game from a corrupted JSON file."""
        with open(self.save_filename, 'w') as f:
            f.write("this is not valid json")
        
        loaded_colony = load_game(self.save_filename)
        self.assertIsNone(loaded_colony)

if __name__ == '__main__':
    unittest.main()
