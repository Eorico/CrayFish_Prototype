class WaterLogic:
    def __init__(self, phone):
        self.waterCleanliness = 100
        self.phone = phone
        
    def addWater(self):
        if self.waterCleanliness >= 100:
            if self.phone:
                self.phone.notify("Water is already full!")
            return
        
    def cleanWater(self):
        if self.waterCleanliness >= 70:
            if self.phone:
                self.phone.notify("Water is already cleaned: 70% to 100% again!")
        elif self.waterCleanliness >= 50:
            if self.phone:
                self.phone.notify("Water is already cleaned: 50% to 100% again!")
        elif self.waterCleanliness >= 30:
            if self.phone:
                self.phone.notif("Water is already cleaned: 30% to 100% again!")
        else:
            self.waterCleanliness = 100
            if self.phone:
                self.phone.notify("Water was very dirty below 30% clean it now!")