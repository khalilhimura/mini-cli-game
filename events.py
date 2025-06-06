import random

class Event:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.is_major = False
        self.choices = []

    def apply(self, colony, choice_key=None): # choice_key added for major events
        # For background events, choice_key will be None.
        # For major events, this method will be overridden.
        return f"{self.name}: {self.description} (Effect applied)."

class MinorResourceBoost(Event):
    def __init__(self):
        resource_types = ["Minerals", "Energy", "Food"] # Added Food
        self.resource_type = random.choice(resource_types)
        self.amount = float(random.randint(25, 75)) # Grant a float amount
        super().__init__(
            name="Minor Resource Boost",
            description=f"Discovered a small cache of {self.resource_type}." # Description used if apply not specific
        )

    def apply(self, colony):
        colony.add_resource(self.resource_type, self.amount)
        # Return the description as the primary message for history
        return f"{self.name}: Added {self.amount:.1f} {self.resource_type}."

class SmallResourceDrain(Event):
    def __init__(self):
        resource_types = ["Minerals", "Energy"]
        self.resource_type = random.choice(resource_types)
        self.amount = float(random.randint(10, 30)) # Drain a float amount
        super().__init__(
            name="Small Resource Drain",
            description=f"A minor equipment malfunction caused a small loss of {self.resource_type}."
        )

    def apply(self, colony):
        current_amount = colony.get_resources().get(self.resource_type, 0.0)
        actual_drain = min(self.amount, current_amount) # Don't go below zero
        
        # Use spend_resources for consistency. spend_resources expects a dict.
        # It also checks for sufficient resources, which is good.
        # If we want to ensure it drains even if this specific amount isn't "enough" for a build,
        # we might need a more direct subtraction, but spend_resources is safer.
        # Let's assume spend_resources handles this correctly or we adjust if not.
        # The current spend_resources returns True/False and deducts if True.
        # For a drain, we always want to deduct up to the available amount.
        # Modifying spend_resources to handle this or adding a direct_spend method might be better.
        # For now, let's try to make it work with current spend_resources.
        # If we only want to drain if the colony has the full amount, spend_resources is fine.
        # The requirement "Don't go below zero" implies we should drain what we can.

        if actual_drain > 0: # Only proceed if there's something to drain
             # We need to bypass the typical "cost" check of spend_resources for a drain.
             # Let's directly modify resources for a drain, ensuring it doesn't go negative.
             colony.resources[self.resource_type] = max(0.0, current_amount - actual_drain)

        return f"{self.name}: Lost {actual_drain:.1f} {self.resource_type} due to a malfunction."

class ProductionSpike(Event):
    def __init__(self):
        self.duration_equivalent_seconds = random.randint(20, 60) # Effect equivalent to X seconds of production
        super().__init__(
            name="Production Spike",
            description=f"Temporary surge in production efficiency!"
        )

    def apply(self, colony):
        # Calculate one-time bonus based on current production rates
        # This requires knowing current production rates.
        # For now, let's grant a fixed bonus to Minerals and Energy as a placeholder.
        bonus_minerals = float(random.randint(10,30)) # Placeholder
        bonus_energy = float(random.randint(5,20))   # Placeholder
        
        colony.add_resource("Minerals", bonus_minerals)
        colony.add_resource("Energy", bonus_energy)
        
        return f"{self.name}: Systems surged, granting an instant bonus of {bonus_minerals:.1f} Minerals and {bonus_energy:.1f} Energy."

class SolarFlare(Event):
    def __init__(self):
        super().__init__(
            name="Solar Flare",
            description="An intense solar flare disrupts colony systems."
        )

    def apply(self, colony):
        lost_energy = float(random.randint(20, 40))
        current = colony.get_resources().get("Energy", 0.0)
        actual = min(lost_energy, current)
        if actual > 0:
            colony.resources["Energy"] = max(0.0, current - actual)
        return f"{self.name}: Lost {actual:.1f} Energy due to radiation interference."

class MeteorStrikeWarning(Event):
    def __init__(self):
        super().__init__(
            name="Meteor Strike Warning!",
            description="Scanners detect a meteor shower heading towards the colony!"
        )
        self.is_major = True
        self.choices = [
            {"text": "Attempt to shoot down meteors (Cost: 50 Energy, Risky)", "key": "shoot_down"},
            {"text": "Brace for impact (Minimal cost, damage likely)", "key": "brace"}
        ]

    def apply(self, colony, choice_key): # apply now takes choice_key
        outcome_message = f"{self.name} - "
        if choice_key == "shoot_down":
            cost = {"Energy": 50.0}
            if colony.has_enough_resources(cost):
                colony.spend_resources(cost)
                if random.random() < 0.60: # 60% success
                    bonus_minerals = float(random.randint(20, 50))
                    colony.add_resource("Minerals", bonus_minerals)
                    outcome_message += f"Successfully defended! Gained {bonus_minerals:.1f} Minerals from salvaged meteors."
                else: # 40% failure
                    lost_energy_amount = float(random.randint(30, 60))
                    current_energy = colony.get_resources().get("Energy", 0.0)
                    actual_energy_loss = min(lost_energy_amount, current_energy)
                    if actual_energy_loss > 0:
                        colony.resources["Energy"] = max(0.0, current_energy - actual_energy_loss)
                    outcome_message += f"Defense failed! Lost {actual_energy_loss:.1f} additional Energy. "
                    outcome_message += colony.damage_random_building()
            else:
                outcome_message += "Not enough Energy to attempt defense! Bracing for impact instead. "
                # Fall through to brace logic
                lost_minerals_amount = float(random.randint(50,100))
                current_minerals = colony.get_resources().get("Minerals", 0.0)
                actual_mineral_loss = min(lost_minerals_amount, current_minerals)
                if actual_mineral_loss > 0:
                    colony.resources["Minerals"] = max(0.0, current_minerals - actual_mineral_loss)
                outcome_message += f"Lost {actual_mineral_loss:.1f} Minerals during impact. "
                outcome_message += colony.damage_random_building()

        elif choice_key == "brace":
            if random.random() < 0.30: # 30% no damage
                outcome_message += "Braced for impact. Thankfully, the colony sustained no significant damage."
            else: # 70% moderate damage
                lost_minerals_amount = float(random.randint(25, 75))
                current_minerals = colony.get_resources().get("Minerals", 0.0)
                actual_mineral_loss = min(lost_minerals_amount, current_minerals)
                if actual_mineral_loss > 0:
                    colony.resources["Minerals"] = max(0.0, current_minerals - actual_mineral_loss)
                outcome_message += f"Braced for impact. Lost {actual_mineral_loss:.1f} Minerals. "
                outcome_message += colony.damage_random_building()
        
        return outcome_message
