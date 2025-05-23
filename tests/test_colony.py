import unittest
import sys
sys.path.append('..') # Add the project root to the Python path

from colony import Colony
from buildings import Mine, SolarPanel, HydroponicsFarm, ResearchLab # Import new buildings

class TestColony(unittest.TestCase):
    def setUp(self):
        """Create a fresh Colony instance before each test."""
        # Colony __init__ now sets initial resources, so tests will work against those.
        self.colony = Colony(initial_turn_number=1) 

    def test_initial_resources(self):
        """Check initial values of all resources."""
        # These values are from Colony.__init__
        expected_initial_resources = {
            "Minerals": 50.0, 
            "Energy": 60.0, 
            "Food": 10.0, 
            "ResearchPoints": 0.0
        }
        self.assertEqual(self.colony.get_resources(), expected_initial_resources)
        self.assertEqual(self.colony.turn_number, 1)
        self.assertEqual(self.colony.event_history, [])


    def test_add_resource(self):
        """Test adding all types of resources."""
        initial_minerals = self.colony.get_resources()["Minerals"]
        self.colony.add_resource("Minerals", 50)
        self.assertEqual(self.colony.get_resources()["Minerals"], initial_minerals + 50)
        
        initial_energy = self.colony.get_resources()["Energy"]
        self.colony.add_resource("Energy", 30)
        self.assertEqual(self.colony.get_resources()["Energy"], initial_energy + 30)

        initial_food = self.colony.get_resources()["Food"]
        self.colony.add_resource("Food", 100)
        self.assertEqual(self.colony.get_resources()["Food"], initial_food + 100)

        initial_rp = self.colony.get_resources()["ResearchPoints"]
        self.colony.add_resource("ResearchPoints", 20)
        self.assertEqual(self.colony.get_resources()["ResearchPoints"], initial_rp + 20)

        # Test adding a completely new resource type (if desired behavior)
        self.colony.add_resource("Helium-3", 5) 
        self.assertEqual(self.colony.get_resources().get("Helium-3"), 5)


    def test_spend_resources_sufficient(self):
        """Test spending resources when sufficient, including new types."""
        self.colony.resources = {"Minerals": 100.0, "Energy": 50.0, "Food": 30.0, "ResearchPoints": 10.0}
        
        can_spend = self.colony.spend_resources({"Minerals": 30, "Energy": 20, "Food": 5})
        self.assertTrue(can_spend)
        self.assertEqual(self.colony.get_resources()["Minerals"], 70.0)
        self.assertEqual(self.colony.get_resources()["Energy"], 30.0)
        self.assertEqual(self.colony.get_resources()["Food"], 25.0)

    def test_spend_resources_insufficient(self):
        """Test spending resources when insufficient, including new types."""
        self.colony.resources = {"Minerals": 20.0, "Energy": 50.0, "Food": 10.0}

        can_spend = self.colony.spend_resources({"Minerals": 30, "Energy": 20}) # Not enough Minerals
        self.assertFalse(can_spend) 
        self.assertEqual(self.colony.get_resources()["Minerals"], 20.0) 
        self.assertEqual(self.colony.get_resources()["Energy"], 50.0)   

        can_spend_food = self.colony.spend_resources({"Food": 20}) # Not enough Food
        self.assertFalse(can_spend_food)
        self.assertEqual(self.colony.get_resources()["Food"], 10.0)


    def test_has_enough_resources(self):
        """Test checking for sufficient resources, including new types."""
        self.colony.resources = {"Minerals": 100.0, "Energy": 50.0, "Food": 20.0, "ResearchPoints": 5.0}

        self.assertTrue(self.colony.has_enough_resources({"Minerals": 50, "Energy": 30, "Food": 10}))
        self.assertTrue(self.colony.has_enough_resources({"ResearchPoints": 5.0}))
        self.assertFalse(self.colony.has_enough_resources({"Minerals": 101}))
        self.assertFalse(self.colony.has_enough_resources({"Food": 21}))
        self.assertFalse(self.colony.has_enough_resources({"ResearchPoints": 5.1}))
        self.assertFalse(self.colony.has_enough_resources({"Helium-3": 1})) # Resource not present

    def test_add_building_all_types(self):
        """Test adding all building types."""
        mine_building = Mine()
        self.colony.add_building(mine_building)
        self.assertIn(mine_building, self.colony.get_buildings())
        
        solar_building = SolarPanel()
        self.colony.add_building(solar_building)
        self.assertIn(solar_building, self.colony.get_buildings())

        farm_building = HydroponicsFarm()
        self.colony.add_building(farm_building)
        self.assertIn(farm_building, self.colony.get_buildings())
        
        lab_building = ResearchLab()
        self.colony.add_building(lab_building)
        self.assertIn(lab_building, self.colony.get_buildings())
        
        self.assertEqual(len(self.colony.get_buildings()), 4)


    def test_calculate_production_bonuses_no_buildings(self):
        """Test production bonuses with no buildings."""
        self.assertEqual(self.colony.calculate_production_bonuses(), {})

    def test_calculate_production_bonuses_with_new_buildings(self):
        """Test production bonuses with all building types."""
        self.colony.add_building(Mine()) # +5 Minerals
        self.colony.add_building(SolarPanel()) # +3 Energy
        self.colony.add_building(HydroponicsFarm()) # +2 Food
        self.colony.add_building(ResearchLab()) # +0.5 RP
        self.colony.add_building(Mine()) # Another +5 Minerals

        expected_bonuses = {
            "Minerals": 10.0, 
            "Energy": 3.0, 
            "Food": 2.0, 
            "ResearchPoints": 0.5
        }
        # Production bonuses are float as building bonuses are floats or ints
        # And defaultdict(int) in calculate_production_bonuses will use int if all inputs are int
        # but if any bonus is float, it will be float. Let's ensure our expected are floats.
        # The building bonuses are defined as float or int. The sum will be float if any is float.
        # Mine/Solar bonuses are int, Farm/Lab are float. So result should be float.
        
        actual_bonuses = self.colony.calculate_production_bonuses()
        self.assertAlmostEqual(actual_bonuses.get("Minerals", 0.0), expected_bonuses["Minerals"])
        self.assertAlmostEqual(actual_bonuses.get("Energy", 0.0), expected_bonuses["Energy"])
        self.assertAlmostEqual(actual_bonuses.get("Food", 0.0), expected_bonuses["Food"])
        self.assertAlmostEqual(actual_bonuses.get("ResearchPoints", 0.0), expected_bonuses["ResearchPoints"])


    def test_to_dict_serialization(self):
        """Test the to_dict method includes all resources."""
        # setUp already initializes resources. We can add more for testing.
        self.colony.add_resource("Minerals", 200) # This adds to initial 50.0
        self.colony.add_resource("Energy", 150)   # Adds to initial 60.0
        # Food starts at 10.0, RP at 0.0
        self.colony.add_building(Mine())
        self.colony.add_building(HydroponicsFarm())
        self.colony.turn_number = 10

        expected_dict = {
            "resources": {
                "Minerals": 250.0, 
                "Energy": 210.0, 
                "Food": 10.0,       # Initial value
                "ResearchPoints": 0.0 # Initial value
            },
            "buildings": ["Mine", "Hydroponics Farm"],
            "turn_number": 10
        }
        actual_dict = self.colony.to_dict()
        self.assertEqual(actual_dict["turn_number"], expected_dict["turn_number"])
        self.assertListEqual(sorted(actual_dict["buildings"]), sorted(expected_dict["buildings"]))
        self.assertDictEqual(actual_dict["resources"], expected_dict["resources"])


    def test_add_event_to_history_basic(self):
        """Test adding events to history and checking order."""
        self.colony.add_event_to_history("Event 1")
        self.colony.add_event_to_history("Event 2")
        self.assertEqual(self.colony.event_history, ["Event 2", "Event 1"]) # Newest first

    def test_add_event_to_history_max_limit(self):
        """Test that event history is trimmed to max_history items."""
        max_h = 5 # Test with a smaller max for convenience
        for i in range(max_h + 3): # Add 8 events
            self.colony.add_event_to_history(f"Event {i}", max_history=max_h)
        
        self.assertEqual(len(self.colony.event_history), max_h)
        # Should contain Event 7, Event 6, Event 5, Event 4, Event 3
        self.assertEqual(self.colony.event_history[0], "Event 7") 
        self.assertEqual(self.colony.event_history[max_h-1], "Event 3")

if __name__ == '__main__':
    unittest.main()
