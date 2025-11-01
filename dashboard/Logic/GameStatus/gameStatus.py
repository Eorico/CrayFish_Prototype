from dashboard.Logic.Essentials.essentials import Essentials
import random
from datetime import datetime
from PyQt5.QtCore import QTimer as timer

class GameDayStatus:
    def __init__(self, ui, essentials: Essentials, phone, temperature):
        
        self.ui = ui
        self.essentials = essentials
        self.phone = phone
        self.temperature = temperature
        
        self.timer = timer()
        self.timer.timeout.connect(self.switchDay)
        self.timer.start(30000)
        
    def updateStat(self):
        self.ui.lineEdit_day.setText(str(self.essentials.day))
        self.ui.lineEdit_day_status.setText(self.essentials.status)
    
    def statusOftheDay(self, username):
        self.ui.status_alert_Text.setText(f"WELCOME: {username}")
        self.ui.status_alert_Text.setStyleSheet("""color: green;""")
        timer.singleShot(2000, lambda: self.ui.status_alert_Text.setText(""))
        
        self.ui.lineEdit_day.setText(str(self.essentials.day))
        self.ui.lineEdit_day_status.setText(self.essentials.status)
        
    def newDayEvent(self):
        if not self.phone:
            return
        
        self.temperature.simulateTemp()
        waterCleanliness = self.temperature.waterLogic.waterCleanliness
        temp = self.temperature.temp
        
        eventList = []
        
        if waterCleanliness < 40:
            eventList.append("Warning: water tank cleanliness is getting low!")
        elif waterCleanliness < 70:
            eventList.append("Its a good day to clean your crayfish tank.")
        
        if temp > 32:
            eventList.append("High temperature alert!")
        if temp < 24:
            eventList.append("Temperature is dropping!")
            
        generalEvents = [
            "🦞 Crayfish are exploring energetically this morning!",
            "📦 You might want to check your feed levels.",
            "⚙️ Filter sounds strange — maybe check the pump.",
            "🌿 Plants in the tank look lush today.",
        ]
        
        if random.random() < 0.3:
            eventList.append(random.choice(generalEvents))
        if not eventList:
            eventList.append("Everything looks fine!")
        
        for msg in eventList:
            self.phone.notify(msg)
        
    def switchDay(self):
        currentStatus = self.essentials.status
        
        if currentStatus == "MORNING":
            self.essentials.update("status", "EVENING")
        elif currentStatus == "EVENING":
            self.essentials.update("status", "MORNING")
            self.essentials.update("day", self.essentials.day + 1)
            
            if self.essentials.day > 1:
                self.newDayEvent()
        else:
            self.essentials.update("status", "MORNING")
            
        self.updateStat()
        
    
    