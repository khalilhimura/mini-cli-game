import unittest
import os
import json
from colony import Colony
from game import save_game, load_game, BUILDING_CLASSES
from buildings import Mine, GeothermalPlant # For testing specific building instances
from research import RESEARCH_PROJECTS

class TestGameLoadSave(unittest.TestCase):
    def setUp(self):
        self.save_filename = "test_savegame.json"
        # Ensure no old save file interferes
        if os.path.exists(self.save_filename):
            os.remove(self.save_filename)

    def tearDown(self):
        # Clean up the save file after tests
        if os.path.exists(self.save_filename):
            os.remove(self.save_filename)

    def test_save_load_basic_colony_state(self):
        colony = Colony(initial_turn_number=5)
        colony.resources["Minerals"] = 150.5
        colony.resources["Energy"] = 75.2
        colony.add_building(Mine())
        
        save_game(colony, self.save_filename)
        loaded_colony = load_game(self.save_filename)

        self.assertIsNotNone(loaded_colony)
        self.assertEqual(loaded_colony.turn_number, 5)
        self.assertAlmostEqual(loaded_colony.resources["Minerals"], 150.5)
        self.assertAlmostEqual(loaded_colony.resources["Energy"], 75.2)
        self.assertEqual(len(loaded_colony.buildings), 1)
        self.assertIsInstance(loaded_colony.buildings[0], Mine)

    def test_save_load_building_levels(self):
        colony = Colony()
        mine_instance = Mine()
        colony.add_building(mine_instance) # Mine is at index 0

        # Simulate upgrading the mine
        # Give enough resources for a few upgrades
        colony.resources["Minerals"] = 1000
        colony.resources["Energy"] = 1000 
        
        colony.upgrade_building(0) # Upgrade to level 2
        colony.upgrade_building(0) # Upgrade to level 3
        
        target_level = 3
        self.assertEqual(colony.buildings[0].level, target_level) # Pre-save check

        save_game(colony, self.save_filename)
        loaded_colony = load_game(self.save_filename)

        self.assertIsNotNone(loaded_colony)
        self.assertEqual(len(loaded_colony.buildings), 1)
        self.assertIsInstance(loaded_colony.buildings[0], Mine)
        self.assertEqual(loaded_colony.buildings[0].level, target_level, "Building level not saved/loaded correctly.")

    def test_save_load_research_state(self):
        colony = Colony()
        initial_rp = 500
        colony.resources["ResearchPoints"] = initial_rp
        
        project_to_research_id = "geothermal_power" 
        project_cost = RESEARCH_PROJECTS[project_to_research_id]["cost"]
        
        colony.research_project(project_to_research_id)
        
        self.assertIn(project_to_research_id, colony.completed_research)
        self.assertIn("GeothermalPlant", colony.unlocked_buildings)
        expected_rp_after_research = initial_rp - project_cost
        self.assertAlmostEqual(colony.resources["ResearchPoints"], expected_rp_after_research)

        save_game(colony, self.save_filename)
        loaded_colony = load_game(self.save_filename)

        self.assertIsNotNone(loaded_colony)
        self.assertIn(project_to_research_id, loaded_colony.completed_research, "Completed research not saved/loaded.")
        self.assertIn("GeothermalPlant", loaded_colony.unlocked_buildings, "Unlocked buildings not saved/loaded.")
        self.assertAlmostEqual(loaded_colony.resources["ResearchPoints"], expected_rp_after_research, "ResearchPoints not saved/loaded correctly.")

    def test_load_game_file_not_found(self):
        loaded_colony = load_game("non_existent_save.json")
        self.assertIsNone(loaded_colony)

    def test_save_load_event_history(self):
        colony = Colony()
        colony.add_event_to_history("Test event 1")
        colony.add_event_to_history("Test event 2")
        
        save_game(colony, self.save_filename)
        loaded_colony = load_game(self.save_filename)
        
        self.assertIsNotNone(loaded_colony)
        self.assertEqual(len(loaded_colony.event_history), 2)
        self.assertIn("Test event 1", loaded_colony.event_history)
        self.assertIn("Test event 2", loaded_colony.event_history)
        # Note: Colony adds events to the beginning, so order is reversed from add calls
        self.assertEqual(loaded_colony.event_history[0], "Test event 2")


if __name__ == '__main__':
    unittest.main()
