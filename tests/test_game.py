import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import random # For mocking random.choice/random.random

sys.path.append('..') # Add the project root to the Python path

from colony import Colony
from buildings import Mine, SolarPanel, HydroponicsFarm, ResearchLab # Import new buildings
from game import (
    generate_resources, build_structure, save_game, load_game, 
    trigger_random_event, resolve_major_event, 
    AVAILABLE_EVENT_CLASSES, BUILDING_CLASSES, # Import for direct use/assertion
    BASE_MINERALS_PER_SECOND, BASE_ENERGY_PER_SECOND, BASE_FOOD_PER_SECOND, BASE_RESEARCH_PER_SECOND
)
# Import the events module itself and specific classes for patching/type checking
import events 
from events import MinorResourceBoost, MeteorStrikeWarning 


class TestGame(unittest.TestCase):
    def setUp(self):
        """Create a fresh Colony instance and define save filename before each test."""
        # Colony __init__ now sets initial resources
        self.colony = Colony(initial_turn_number=1) 
        self.save_filename = "test_savegame.json"

    def tearDown(self):
        """Remove the test save file if it exists after each test."""
        if os.path.exists(self.save_filename):
            os.remove(self.save_filename)

    def test_generate_resources_all_types(self):
        """Test base and bonus resource generation for all resource types."""
        time_delta = 1.0

        # Store initial resources (from Colony.__init__)
        initial_minerals = self.colony.resources["Minerals"]
        initial_energy = self.colony.resources["Energy"]
        initial_food = self.colony.resources["Food"]
        initial_rp = self.colony.resources["ResearchPoints"]
        
        # Test base generation first
        generate_resources(self.colony, time_delta)
        self.assertAlmostEqual(self.colony.resources["Minerals"], initial_minerals + BASE_MINERALS_PER_SECOND * time_delta)
        self.assertAlmostEqual(self.colony.resources["Energy"], initial_energy + BASE_ENERGY_PER_SECOND * time_delta)
        self.assertAlmostEqual(self.colony.resources["Food"], initial_food + BASE_FOOD_PER_SECOND * time_delta)
        self.assertAlmostEqual(self.colony.resources["ResearchPoints"], initial_rp + BASE_RESEARCH_PER_SECOND * time_delta)

        # Reset resources for bonus test for clarity, or accumulate
        # For simplicity, let's accumulate from the previous state.
        current_minerals = self.colony.resources["Minerals"]
        current_energy = self.colony.resources["Energy"]
        current_food = self.colony.resources["Food"]
        current_rp = self.colony.resources["ResearchPoints"]

        # Add buildings and test bonus generation
        self.colony.add_building(Mine()) # +5 Minerals/sec
        self.colony.add_building(HydroponicsFarm()) # +2 Food/sec
        self.colony.add_building(ResearchLab()) # +0.5 RP/sec
        
        generate_resources(self.colony, time_delta)
        
        expected_minerals = current_minerals + (BASE_MINERALS_PER_SECOND + 5.0) * time_delta
        expected_energy = current_energy + (BASE_ENERGY_PER_SECOND + 0.0) * time_delta # No new energy building
        expected_food = current_food + (BASE_FOOD_PER_SECOND + 2.0) * time_delta
        expected_rp = current_rp + (BASE_RESEARCH_PER_SECOND + 0.5) * time_delta
        
        self.assertAlmostEqual(self.colony.resources["Minerals"], expected_minerals)
        self.assertAlmostEqual(self.colony.resources["Energy"], expected_energy)
        self.assertAlmostEqual(self.colony.resources["Food"], expected_food)
        self.assertAlmostEqual(self.colony.resources["ResearchPoints"], expected_rp)


    def test_build_structure_new_buildings(self):
        """Test successful construction of new building types."""
        # HydroponicsFarm
        farm_cost = HydroponicsFarm().cost
        self.colony.resources["Minerals"] = farm_cost["Minerals"] # Give exactly enough
        self.colony.resources["Energy"] = farm_cost["Energy"]
        initial_minerals = self.colony.resources["Minerals"]
        initial_energy = self.colony.resources["Energy"]

        build_success_farm = build_structure(self.colony, HydroponicsFarm)
        self.assertTrue(build_success_farm)
        self.assertEqual(len(self.colony.get_buildings()), 1)
        self.assertIsInstance(self.colony.get_buildings()[0], HydroponicsFarm)
        self.assertEqual(self.colony.resources["Minerals"], initial_minerals - farm_cost["Minerals"])
        self.assertEqual(self.colony.resources["Energy"], initial_energy - farm_cost["Energy"])

        # ResearchLab
        self.colony.buildings = [] # Clear buildings for next test
        lab_cost = ResearchLab().cost
        self.colony.resources["Minerals"] = lab_cost["Minerals"] # Give exactly enough
        self.colony.resources["Energy"] = lab_cost["Energy"]
        initial_minerals = self.colony.resources["Minerals"]
        initial_energy = self.colony.resources["Energy"]

        build_success_lab = build_structure(self.colony, ResearchLab)
        self.assertTrue(build_success_lab)
        self.assertEqual(len(self.colony.get_buildings()), 1)
        self.assertIsInstance(self.colony.get_buildings()[0], ResearchLab)
        self.assertEqual(self.colony.resources["Minerals"], initial_minerals - lab_cost["Minerals"])
        self.assertEqual(self.colony.resources["Energy"], initial_energy - lab_cost["Energy"])

    @patch('game.random.random')   # Corresponds to mock_game_rr in signature
    @patch('game.random.choice')   # Corresponds to mock_game_rc in signature
    def test_trigger_background_event_food_boost(self, mock_game_rc, mock_game_rr): # mock_game_rc is for choice, mock_game_rr for random
        """Test triggering a MinorResourceBoost for Food by controlling MinorResourceBoost.__init__."""
        mock_game_rr.return_value = 0.10  # Ensures event triggers (is < 0.15 in game.py)
        mock_game_rc.return_value = MinorResourceBoost  # game.random.choice returns MinorResourceBoost class

        fixed_boost_amount = 50.0
        
        original_mrb_init = events.MinorResourceBoost.__init__ # Save original

        def mock_mrb_init(self_mrb_instance):
            # Call Event.__init__ to set up .name, .description, .is_major, .choices
            events.Event.__init__(self_mrb_instance, 
                                  name="Minor Resource Boost", 
                                  description="A controlled boost of Food occurred.") # Generic desc
            self_mrb_instance.resource_type = "Food" # Explicitly set resource type
            self_mrb_instance.amount = fixed_boost_amount # Explicitly set amount
        
        # Patch __init__ of the MinorResourceBoost class in the events module
        with patch.object(events.MinorResourceBoost, '__init__', new=mock_mrb_init):
            initial_food = self.colony.resources["Food"]
            initial_history_len = len(self.colony.event_history)

            returned_event = trigger_random_event(self.colony, AVAILABLE_EVENT_CLASSES)
            
            self.assertIsNone(returned_event) # Background events should return None
            self.assertEqual(self.colony.resources["Food"], initial_food + fixed_boost_amount)
            self.assertEqual(len(self.colony.event_history), initial_history_len + 1)
            # Check message content based on MinorResourceBoost.apply()
            # Apply method: return f"{self.name}: Added {self.amount:.1f} {self.resource_type}."
            self.assertIn(f"Added {fixed_boost_amount:.1f} Food", self.colony.event_history[0])
            self.assertIn("Minor Resource Boost", self.colony.event_history[0])


    @patch('game.random.random')   # Outer decorator, maps to mock_game_rr
    @patch('game.random.choice')   # Inner decorator, maps to mock_game_rc
    def test_trigger_major_event_meteor_strike(self, mock_game_rc, mock_game_rr):
        """Test triggering a MeteorStrikeWarning major event."""
        # mock_game_rc is for 'game.random.choice'
        # mock_game_rr is for 'game.random.random'
        
        mock_game_rr.return_value = 0.10 # Ensure event triggers (is < 0.15)
        mock_game_rc.return_value = MeteorStrikeWarning # Force MeteorStrikeWarning

        initial_history_len = len(self.colony.event_history)
        
        event_instance = trigger_random_event(self.colony, AVAILABLE_EVENT_CLASSES)
        
        self.assertIsNotNone(event_instance)
        self.assertIsInstance(event_instance, MeteorStrikeWarning)
        self.assertTrue(event_instance.is_major)
        self.assertEqual(len(self.colony.event_history), initial_history_len) # History not logged until resolved


    @patch('events.random.random') # Patch random.random used in MeteorStrikeWarning.apply
    def test_resolve_major_event_meteor_strike_shoot_down_success(self, mock_apply_random):
        """Test resolving MeteorStrikeWarning: shoot_down success."""
        mock_apply_random.return_value = 0.50 # Ensures success (random < 0.60)
        
        event = MeteorStrikeWarning()
        initial_energy = 100.0
        initial_minerals = 50.0
        self.colony.resources = {"Minerals": initial_minerals, "Energy": initial_energy, "Food": 10.0, "ResearchPoints": 0.0}
        
        resolve_major_event(self.colony, event, "shoot_down")
        
        self.assertAlmostEqual(self.colony.resources["Energy"], initial_energy - 50.0) # Cost of shooting
        self.assertTrue(self.colony.resources["Minerals"] > initial_minerals) # Gained minerals
        self.assertIn("Successfully defended", self.colony.event_history[0])

    @patch('events.random.random') # Patch random.random used in MeteorStrikeWarning.apply
    def test_resolve_major_event_meteor_strike_shoot_down_fail(self, mock_apply_random):
        """Test resolving MeteorStrikeWarning: shoot_down failure."""
        mock_apply_random.return_value = 0.70 # Ensures failure (random >= 0.60)
        
        event = MeteorStrikeWarning()
        initial_energy = 100.0
        initial_minerals = 50.0
        self.colony.resources = {"Minerals": initial_minerals, "Energy": initial_energy, "Food": 10.0, "ResearchPoints": 0.0}
        
        resolve_major_event(self.colony, event, "shoot_down")
        
        # Energy spent for attempt, then additional energy lost (random amount)
        # Minerals unchanged or potentially reduced if secondary damage was modeled (not in current event)
        self.assertTrue(self.colony.resources["Energy"] < initial_energy - 50.0 + 0.001) # Energy is less than initial - attempt cost
        self.assertAlmostEqual(self.colony.resources["Minerals"], initial_minerals) # No mineral gain on failure
        self.assertIn("Defense failed", self.colony.event_history[0])


    def test_save_and_load_game_all_resources_and_buildings(self):
        """Test saving and loading with all resources and new buildings."""
        self.colony.resources = {
            "Minerals": 111.1, "Energy": 222.2, "Food": 33.3, "ResearchPoints": 4.4
        }
        self.colony.add_building(Mine())
        self.colony.add_building(SolarPanel())
        self.colony.add_building(HydroponicsFarm())
        self.colony.add_building(ResearchLab())
        self.colony.turn_number = 15

        original_resources = self.colony.get_resources().copy()
        original_building_names = sorted([b.name for b in self.colony.get_buildings()])
        original_turn_number = self.colony.turn_number

        save_game(self.colony, self.save_filename)
        self.assertTrue(os.path.exists(self.save_filename))

        loaded_colony = load_game(self.save_filename)
        self.assertIsNotNone(loaded_colony)

        # Verify all four resources
        self.assertAlmostEqual(loaded_colony.resources["Minerals"], original_resources["Minerals"])
        self.assertAlmostEqual(loaded_colony.resources["Energy"], original_resources["Energy"])
        self.assertAlmostEqual(loaded_colony.resources["Food"], original_resources["Food"])
        self.assertAlmostEqual(loaded_colony.resources["ResearchPoints"], original_resources["ResearchPoints"])
        
        loaded_building_names = sorted([b.name for b in loaded_colony.get_buildings()])
        self.assertListEqual(loaded_building_names, original_building_names)
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
