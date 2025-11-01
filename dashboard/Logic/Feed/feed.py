from PyQt5.QtCore import QTimer as timer

class CrayFishFeeder:
    def __init__(self, ui, essentials, phone):
        self.ui = ui
        self.essentials = essentials
        self.phone = phone
        self.growthRed = 1
        self.growthblue = 1
        
    def feedCrayfish(self):
        if self.essentials.feeds <= 0:
            self.ui.status_alert_Text.setText("No more feeds available!")
            timer.singleShot(2000, lambda: self.ui.status_alert_Text.setText(""))
            return
        
        self.essentials.update("feeds", self.essentials.feeds - 1)
        
        self.essentials.update("crayfish_Red", self.essentials.crayFish_Red + self.growthRed)
        self.essentials.update("crayfish_Blue", self.essentials.crayFish_Blue + self.growthblue)
        self.essentials.update("total_Crayfish", self.essentials.crayFish_Red + self.essentials.crayFish_Blue)
        
        self.ui.lineEdit_feeds.setText(str(self.essentials.feeds))
        self.ui.lineEdit_money_2.setText(str(self.essentials.totalCrayFish))
        
        self.ui.status_alert_Text.setText("Crayfish have been fed!")
        timer.singleShot(2000, lambda: self.ui.status_alert_Text.setText(""))
        
        
        
class CrayFishBoostFeeder:
    def __init__(self, ui, essentials, phone):
        self.ui = ui
        self.essentials = essentials
        self.phone = phone
        self.growthRed = 1
        self.growthblue = 1
        
    def boostFeedCrayfish(self):
        if self.essentials.boosters <= 0:
            self.ui.status_alert_Text.setText("No boosters available!")
            timer.singleShot(2000, lambda: self.ui.status_alert_Text.setText(""))
            return
        
        self.growthblue = 3
        self.growthRed = 3
        self.essentials.update("boosters", self.essentials.boosters - 1)
        self.essentials.update("crayfish_Red", self.essentials.crayFish_Red + self.growthRed)
        self.essentials.update("crayfish_Blue", self.essentials.crayFish_Blue + self.growthblue)
        self.essentials.update("total_Crayfish", self.essentials.crayFish_Red + self.essentials.crayFish_Blue)
        
        self.ui.lineEdit_booster.setText(str(self.essentials.boosters))
        self.ui.lineEdit_money_2.setText(str(self.essentials.totalCrayFish))
        
        self.ui.status_alert_Text.setText("Crayfish growth Boosted!")
        timer.singleShot(2000, lambda: self.ui.status_alert_Text.setText(""))