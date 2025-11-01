from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication, QMessageBox
from PyQt5.QtCore import QTimer as timer
from Designer_Files.ui.dashboard_ui import Ui_MainWindow as DASH_MAIN 
from dashboard.Logic.Inventory.inventory import Inventory

from dashboard.Animation.animation import *

from dashboard.Widget.invetoryWidget.inventoryWidget import InventoryWidget
from dashboard.Widget.marketWidget.marketWidget import MarketWidget
from dashboard.Widget.phoneWidget.phoneWidget import PhoneWidget
from dashboard.Widget.MachineWidget.machineWidget import MachineWidget

from dashboard.Logic.Phone.phone_notif import Phone
from dashboard.Logic.Market.Market import Market
from dashboard.Logic.Machine.machineLearning_Sample import MachineLearning

from dashboard.Logic.AbstractMethods.WidgetAbs import OpenWidgetBtn
from dashboard.Logic.Essentials.essentials import Essentials
from dashboard.Logic.GameStatus.gameStatus import GameDayStatus
from dashboard.Logic.Temperature.temperature import Temperature
from dashboard.Logic.Feed.feed import CrayFishFeeder as feed
from dashboard.Logic.Feed.feed import CrayFishBoostFeeder as booster

import sys

def openWindow(w:OpenWidgetBtn):
    w.OpenWindow()        

    
class DashboardWindow(MAIN, DASH_MAIN):
    def __init__(self, username, email, idToken):
        super().__init__()
        self.setupUi(self)
        
        self.phone = Phone()
        self.phoneWid = PhoneWidget(self.phone)
        self.phone.newPhoneNotif.connect(self.phoneNotifValueDashboard)
        self.phone.notify("Phone connected successfully!")
        
        self.inv = Inventory()
        self.inventoryWid = InventoryWidget(self.inv)
    
            
        self.pushButton.clicked.connect(self.resetPhoneValueDashboard)
        
        
        self.username = username
        self.email = email
        
        self.animation = CrayFishAnimation(self)
        self.animation.initCrayfish()
        
        self.Logout_btn.clicked.connect(self.LogoutDashBoard)
        
        self.essentials = Essentials(email, idToken)
        self.essentials.dataUpdated.connect(self.alertDashboard)
        
        self.temperature = Temperature(self.phone)
        
        self.gameDaystatus = GameDayStatus(self, self.essentials, self.phone, self.temperature)
        self.gameDaystatus.statusOftheDay(username)
        
        self.lineEdit_money.setText(str(self.essentials.money))
        self.lineEdit_feeds.setText(str(self.essentials.feeds))
        self.lineEdit_booster.setText(str(self.essentials.boosters))
        self.lineEdit_money_2.setText(str(self.essentials.totalCrayFish))
        
        self.inv.lineEdit_blueCray_amount.setText(str(self.essentials.crayFish_Blue))
        self.inv.lineEdit_redCray_amount.setText(str(self.essentials.crayFish_Red))
        self.inv.lineEdit_feed_amount.setText(str(self.essentials.feeds))
        self.inv.lineEdit_booster_amount.setText(str(self.essentials.boosters))
        self.lineEdit_money_2.setText(str(self.essentials.totalCrayFish))
        
        self.feed = feed(self, self.essentials, self.phone)
        self.booster = booster(self, self.essentials, self.phone)
        self.feed_btn.clicked.connect(self.feed.feedCrayfish)
        self.boost_btn.clicked.connect(self.booster.boostFeedCrayfish)
        
        self.market = Market(self, self.essentials)
        self.marketWid = MarketWidget(self.market)
        
        self.machineLrn = MachineLearning()
        self.machineLearnWid = MachineWidget(self.machineLrn)
        self.machineLrn.hide()
        
        self.windows = [
            self.phoneWid, 
            self.marketWid, 
            self.inventoryWid,
            self.machineLearnWid
        ]
        
        self.windBtn = [
            self.pushButton, self.market_btn, self.inventory_btn, self.pushButton_CAM
        ]
        
        for btn, win in zip(self.windBtn, self.windows):
            btn.clicked.connect(lambda _, w=win: openWindow(w))
        
    def alertDashboard(self, message):
        self.status_alert_Text.setText(message)
        timer.singleShot(2000, lambda: self.status_alert_Text.setText(""))
        
    def phoneNotifValueDashboard(self):
        try:
            current = int(self.lineEdit_money_3.text() or 0)
            self.lineEdit_money_3.setText(str(current+1))
        except Exception as e:
            self.lineEdit_money_3.setText("1")
            
    def resetPhoneValueDashboard(self):
        self.lineEdit_money_3.setText("0")
        
    def LogoutDashBoard(self):
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.animation.stopAnimation()   
            try:
                if hasattr(self.gameDaystatus, 'timer') and self.gameDaystatus.timer.isActive():
                    self.gameDaystatus.timer.stop()
                    print(f"Game is paused!, user: {self.username} logs out")
            except Exception as e:
                print(f"Error: {e}")
             
            try:    
                self.essentials.saveUserData()
                print("Progress saved successfully.")
            except Exception as e:
                print(f"Error: {e}")
        
            from main import AuthWindow
            self.authWindow = AuthWindow()
            self.authWindow.show()
            self.close()
        
        else:
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
