from config.firebase_config import db
from PyQt5.QtCore import pyqtSignal, QObject
import random

class Essentials(QObject):
    dataUpdated = pyqtSignal(str)
    def __init__(self, email, idToken):
        super().__init__()
        self.email = email
        self.idToken = idToken
        self.userKey = email.replace(".", "_")

        self._money = random.randint(1, 100)
        self._feeds = random.randint(1, 20)
        self._boosters = 0
        self._day = 1
        self._status = "MORNING"
        self._crayFish_Red = random.randint(1, 4)
        self._crayFish_Blue = random.randint(1, 4)

        try:
            data = db.child("users").child(self.userKey).get(self.idToken).val()
            if data:
                self._money = data.get("money", 0)
                self._feeds = data.get("feeds", 0)
                self._boosters = data.get("boosters", 0)
                self._day = data.get("day", 1)

                raw_status = data.get("status", "MORNING")
                if isinstance(raw_status, int):
                    self._status = "MORNING" if raw_status == 1 else "EVENING"
                elif isinstance(raw_status, str):
                    self._status = raw_status.upper()
                else:
                    self._status = "MORNING"

                self._crayFish_Red = data.get("crayFish_Red", 0)
                self._crayFish_Blue = data.get("crayFish_Blue", 0)
            else:
                self.saveUserData()

            print(f"Loaded Essentials for {self.email}")

        except Exception as e:
            print(f"Error loading user essentials: {e}")

    @property
    def money(self): return self._money
    @property
    def feeds(self): return self._feeds
    @property
    def boosters(self): return self._boosters
    @property
    def day(self): return self._day
    @property
    def status(self): return self._status
    @property
    def crayFish_Red(self): return self._crayFish_Red
    @property
    def crayFish_Blue(self): return self._crayFish_Blue
    @property
    def totalCrayFish(self): return self._crayFish_Red + self._crayFish_Blue

    def saveUserData(self):
        try:
            db.child("users").child(self.userKey).set({
                "money": self._money,
                "feeds": self._feeds,
                "boosters": self._boosters,
                "day": self._day,
                "status": self._status,  
                "crayFish_Red": self._crayFish_Red,
                "crayFish_Blue": self._crayFish_Blue,
                "total_Crayfish": self.totalCrayFish
            }, self.idToken)
            print(f"Data saved for {self.email}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def update(self, key, value):
        try:
            if key == "status":
                if isinstance(value, int):
                    value = "MORNING" if value == 1 else "EVENING"
                elif isinstance(value, str):
                    value = value.upper()
                else:
                    value = "MORNING"

            match key:
                case "money": self._money = value
                case "feeds": self._feeds = value
                case "boosters": self._boosters = value
                case "day": self._day = value
                case "status": self._status = value
                case "crayFish_Red": self._crayFish_Red = value
                case "crayFish_Blue": self._crayFish_Blue = value

            self.saveUserData()
            print(f"Updated {key} to {value} for {self.email}")
            self.dataUpdated.emit(f"{key.upper()} updated to {value}")
        except Exception as e:
            print(f"Error updating {key}: {e}")
