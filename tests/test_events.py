import unittest
import random

from colony import Colony
from buildings import Mine
from events import SolarFlare

class TestEventConsequences(unittest.TestCase):
    def test_damage_random_building_downgrade(self):
        colony = Colony()
        mine = Mine()
        mine.level = 2
        colony.add_building(mine)
        random.seed(1)
        msg = colony.damage_random_building()
        self.assertIn("damaged", msg)
        self.assertEqual(colony.buildings[0].level, 1)

    def test_damage_random_building_destroy(self):
        colony = Colony()
        mine = Mine()
        colony.add_building(mine)
        random.seed(1)
        msg = colony.damage_random_building()
        self.assertIn("destroyed", msg)
        self.assertEqual(len(colony.buildings), 0)

    def test_solar_flare_energy_loss(self):
        colony = Colony()
        colony.resources["Energy"] = 50.0
        random.seed(1)
        event = SolarFlare()
        message = event.apply(colony)
        self.assertIn("Lost", message)
        self.assertLess(colony.resources["Energy"], 50.0)

if __name__ == '__main__':
    unittest.main()
