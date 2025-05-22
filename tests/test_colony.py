import unittest
import sys
sys.path.append('..') # Add the project root to the Python path

from colony import Colony
from buildings import Mine, SolarPanel

class TestColony(unittest.TestCase):
    def setUp(self):
        """Create a fresh Colony instance before each test."""
        self.colony = Colony(initial_turn_number=1) # Ensure turn number is also fresh

    def test_initial_resources(self):
        """Check initial resources are zero."""
        self.assertEqual(self.colony.get_resources(), {"Minerals": 0, "Energy": 0})
        self.assertEqual(self.colony.turn_number, 1)

    def test_add_resource(self):
        """Test adding resources."""
        self.colony.add_resource("Minerals", 50)
        self.assertEqual(self.colony.get_resources()["Minerals"], 50)
        self.colony.add_resource("Minerals", 20)
        self.assertEqual(self.colony.get_resources()["Minerals"], 70)
        self.colony.add_resource("Energy", 30)
        self.assertEqual(self.colony.get_resources()["Energy"], 30)
        # Test adding a new resource type (if desired behavior, though current Colony starts with both)
        self.colony.add_resource("Food", 100) # Assuming this is handled gracefully
        self.assertEqual(self.colony.get_resources().get("Food"), 100)


    def test_spend_resources_sufficient(self):
        """Test spending resources when sufficient."""
        self.colony.add_resource("Minerals", 100)
        self.colony.add_resource("Energy", 50)
        
        can_spend = self.colony.spend_resources({"Minerals": 30, "Energy": 20})
        self.assertTrue(can_spend)
        self.assertEqual(self.colony.get_resources()["Minerals"], 70)
        self.assertEqual(self.colony.get_resources()["Energy"], 30)

    def test_spend_resources_insufficient(self):
        """Test spending resources when insufficient."""
        self.colony.add_resource("Minerals", 20) # Not enough for the 30 required
        self.colony.add_resource("Energy", 50)

        can_spend = self.colony.spend_resources({"Minerals": 30, "Energy": 20})
        self.assertFalse(can_spend) # spend_resources should return False
        self.assertEqual(self.colony.get_resources()["Minerals"], 20) # Resources unchanged
        self.assertEqual(self.colony.get_resources()["Energy"], 50)   # Resources unchanged

    def test_has_enough_resources(self):
        """Test checking for sufficient resources."""
        self.colony.add_resource("Minerals", 100)
        self.colony.add_resource("Energy", 50)

        self.assertTrue(self.colony.has_enough_resources({"Minerals": 50, "Energy": 30}))
        self.assertTrue(self.colony.has_enough_resources({"Minerals": 100, "Energy": 50}))
        self.assertFalse(self.colony.has_enough_resources({"Minerals": 101}))
        self.assertFalse(self.colony.has_enough_resources({"Energy": 51}))
        self.assertFalse(self.colony.has_enough_resources({"Minerals": 50, "Energy": 51}))
        self.assertFalse(self.colony.has_enough_resources({"Food": 1})) # Resource not present

    def test_add_building(self):
        """Test adding a building."""
        mine_building = Mine()
        self.colony.add_building(mine_building)
        self.assertEqual(len(self.colony.get_buildings()), 1)
        self.assertIsInstance(self.colony.get_buildings()[0], Mine)
        self.assertEqual(self.colony.get_buildings()[0].name, "Mine")

        solar_building = SolarPanel()
        self.colony.add_building(solar_building)
        self.assertEqual(len(self.colony.get_buildings()), 2)
        self.assertIsInstance(self.colony.get_buildings()[1], SolarPanel)


    def test_calculate_production_bonuses_no_buildings(self):
        """Test production bonuses with no buildings."""
        # The current implementation of calculate_production_bonuses returns defaultdict(int)
        # which becomes a dict. If no bonuses, it's an empty dict.
        self.assertEqual(self.colony.calculate_production_bonuses(), {})

    def test_calculate_production_bonuses_with_buildings(self):
        """Test production bonuses with multiple buildings."""
        self.colony.add_building(Mine())
        self.colony.add_building(SolarPanel())
        self.colony.add_building(Mine()) # Add a second mine

        expected_bonuses = {"Minerals": 10, "Energy": 3} # 2 Mines * 5 + 1 SolarPanel * 3
        self.assertEqual(self.colony.calculate_production_bonuses(), expected_bonuses)

    def test_to_dict_serialization(self):
        """Test the to_dict method for serialization preparedness."""
        self.colony.add_resource("Minerals", 200)
        self.colony.add_resource("Energy", 150)
        self.colony.add_building(Mine())
        self.colony.add_building(SolarPanel())
        self.colony.turn_number = 10

        expected_dict = {
            "resources": {"Minerals": 200, "Energy": 150},
            "buildings": ["Mine", "Solar Panel"],
            "turn_number": 10
        }
        self.assertEqual(self.colony.to_dict(), expected_dict)

if __name__ == '__main__':
    unittest.main()
