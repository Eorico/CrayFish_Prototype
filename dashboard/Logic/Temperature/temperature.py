from dashboard.Logic.Water.waterLogic import WaterLogic
import random

class Temperature:
    def __init__(self, phone):
        self.temp = 28.0
        self.phone = phone
        self.waterLogic = WaterLogic(self.phone)
        
    def simulateTemp(self):
        self.temp += random.choice([-0.5, 0.2, 0.8])
        self.waterLogic.waterCleanliness -= random.randint(1, 4)
        
        self.temp = max(20, min(35, self.temp))
        self.waterLogic.waterCleanliness = max(0, min(100, self.waterLogic.waterCleanliness))
        
        if self.waterLogic.waterCleanliness < 30:
            if self.phone:
                self.phone.notify("ALert: cleanliness critically low (30%)!")
            return
        elif self.temp > 32:
            if self.phone:
                self.phone.notify("Warning: water temperature too high (32^C)!")
            return
        elif self.temp < 24:
            if self.phone:
                self.phone.notify("Warning: water temperature too low (24^C)!")
            return
        
        if random.random() < 0.2:
            behavior = random.choice([
                "🦞Crayfish are playing near the rocks.",
                "🦞Crayfish are hiding under the plants.",
                "🦞Crayfish are fighting over food.",
                "🦞Crayfish are exploring the tank."
            ])
            if self.phone:
                self.phone.notify(behavior)