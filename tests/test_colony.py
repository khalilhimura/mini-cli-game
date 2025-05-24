import unittest
from colony import Colony
from buildings import Mine, SolarPanel, ResearchLab # Assuming ResearchLab is a default building
from research import RESEARCH_PROJECTS

class TestBuildingUpgrades(unittest.TestCase):
    def setUp(self):
        self.colony = Colony()

    def test_initial_building_level(self):
        mine = Mine()
        self.colony.add_building(mine)
        self.assertEqual(self.colony.buildings[0].level, 1)

    def test_upgrade_building_sufficient_resources(self):
        mine = Mine()
        self.colony.add_building(mine)
        initial_minerals = 1000
        initial_energy = 500
        self.colony.resources["Minerals"] = initial_minerals
        self.colony.resources["Energy"] = initial_energy
        
        upgrade_cost = self.colony.buildings[0].upgrade_cost() # Cost for level 1 to 2

        success = self.colony.upgrade_building(0)
        self.assertTrue(success)
        self.assertEqual(self.colony.buildings[0].level, 2)
        self.assertEqual(self.colony.resources["Minerals"], initial_minerals - upgrade_cost["Minerals"])
        self.assertEqual(self.colony.resources["Energy"], initial_energy - upgrade_cost["Energy"])
        self.assertIn(f"{mine.name} upgraded to level 2", self.colony.event_history[0])

    def test_upgrade_building_insufficient_resources(self):
        mine = Mine()
        self.colony.add_building(mine)
        self.colony.resources["Minerals"] = 0 # Insufficient
        self.colony.resources["Energy"] = 0  # Insufficient

        original_minerals = self.colony.resources["Minerals"]
        original_energy = self.colony.resources["Energy"]

        success = self.colony.upgrade_building(0)
        self.assertFalse(success)
        self.assertEqual(self.colony.buildings[0].level, 1)
        self.assertEqual(self.colony.resources["Minerals"], original_minerals)
        self.assertEqual(self.colony.resources["Energy"], original_energy)
        self.assertIn(f"Not enough resources to upgrade {mine.name}", self.colony.event_history[0])

    def test_production_bonus_increases_with_level(self):
        mine = Mine()
        self.colony.add_building(mine)
        
        initial_bonus = self.colony.calculate_production_bonuses().get("Minerals", 0)

        self.colony.resources["Minerals"] = 1000
        self.colony.resources["Energy"] = 500
        self.colony.upgrade_building(0)

        new_bonus = self.colony.calculate_production_bonuses().get("Minerals", 0)
        self.assertGreater(new_bonus, initial_bonus)

    def test_upgrade_cost_increases_with_level(self):
        mine = Mine()
        self.colony.add_building(mine)
        
        cost_lvl_1_to_2 = mine.upgrade_cost()

        self.colony.resources["Minerals"] = 1000
        self.colony.resources["Energy"] = 500
        self.colony.upgrade_building(0) # Upgrade to level 2

        cost_lvl_2_to_3 = mine.upgrade_cost() # mine instance is updated
        
        self.assertGreater(cost_lvl_2_to_3["Minerals"], cost_lvl_1_to_2["Minerals"])
        self.assertGreater(cost_lvl_2_to_3["Energy"], cost_lvl_1_to_2["Energy"])


class TestResearchSystem(unittest.TestCase):
    def setUp(self):
        self.colony = Colony()
        # RESEARCH_PROJECTS is imported at the top

    def test_initial_unlocked_buildings(self):
        self.assertIn("Mine", self.colony.unlocked_buildings)
        self.assertIn("Solar Panel", self.colony.unlocked_buildings)
        self.assertIn("Hydroponics Farm", self.colony.unlocked_buildings)
        self.assertIn("Research Lab", self.colony.unlocked_buildings)
        self.assertNotIn("GeothermalPlant", self.colony.unlocked_buildings)

    def test_research_project_sufficient_research_points(self):
        self.colony.resources["ResearchPoints"] = 300
        project_id = "geothermal_power"
        project_details = RESEARCH_PROJECTS[project_id]
        
        initial_rp = self.colony.resources["ResearchPoints"]
        
        success = self.colony.research_project(project_id)
        self.assertTrue(success)
        self.assertIn(project_id, self.colony.completed_research)
        self.assertIn("GeothermalPlant", self.colony.unlocked_buildings)
        self.assertEqual(self.colony.resources["ResearchPoints"], initial_rp - project_details["cost"])
        self.assertIn(f"Research complete: {project_details['name']}", self.colony.event_history[0])

    def test_research_project_insufficient_research_points(self):
        self.colony.resources["ResearchPoints"] = 50 # Insufficient for geothermal_power (cost 250)
        project_id = "geothermal_power"
        project_details = RESEARCH_PROJECTS[project_id]
        initial_rp = self.colony.resources["ResearchPoints"]

        success = self.colony.research_project(project_id)
        self.assertFalse(success)
        self.assertNotIn(project_id, self.colony.completed_research)
        self.assertNotIn("GeothermalPlant", self.colony.unlocked_buildings)
        self.assertEqual(self.colony.resources["ResearchPoints"], initial_rp)
        self.assertIn(f"Not enough Research Points for '{project_details['name']}'", self.colony.event_history[0])

    def test_research_project_already_completed(self):
        self.colony.resources["ResearchPoints"] = 300
        project_id = "geothermal_power"
        project_name = RESEARCH_PROJECTS[project_id]['name']
        
        self.colony.research_project(project_id) # First time
        
        current_rp_after_first_research = self.colony.resources["ResearchPoints"]
        self.colony.event_history.clear() # Clear history to check next message

        success = self.colony.research_project(project_id) # Second time
        self.assertFalse(success) # Should indicate not "successful" in terms of new research
        self.assertEqual(self.colony.resources["ResearchPoints"], current_rp_after_first_research)
        self.assertIn(f"Project '{project_name}' already researched", self.colony.event_history[0])

    def test_research_invalid_project_id(self):
        project_id = "non_existent_project"
        success = self.colony.research_project(project_id)
        self.assertFalse(success)
        self.assertIn(f"Error: Research project '{project_id}' not found", self.colony.event_history[0])

if __name__ == '__main__':
    unittest.main()
