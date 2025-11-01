from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication, QPushButton, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QTimer as timer
from Designer_Files.ui.market_ui import Ui_Form as MARKET_UI
import sys, random

class Market(MAIN, MARKET_UI):
    def __init__(self, ui, essentials):
        super().__init__()
        self.setupUi(self)
        
        self.ui = ui
        self.essentials = essentials
        
        self.items = [
                "🦞Crayfish Red",
                "🦞Crayfish Blue",
                "🧪Booster"
        ]
        
        self.prices = {
            "🦞Crayfish Red": random.randint(15, 30),
            "🦞Crayfish Blue": random.randint(25, 50),
            "🧪Booster": 150
        }
        
        self.marketTable()
        
        self.marketTimer = timer()
        self.marketTimer.timeout.connect(self.marketUpdatePrices)
        self.marketTimer.start(30000)
        
    def marketTable(self):
        table = self.tableWidget_market
        table.setRowCount(len(self.items))
        
        for row, itemName in enumerate(self.items):
            table.setItem(row, 0, self._marketCreateTableItem(itemName))
            
            price = self.prices[itemName]
            table.setItem(row, 1, self._marketCreateTableItem(f"{price} ₱"))
            
            buyButton = QPushButton("Buy")
            buyButton.setStyleSheet(""" QPushButton { background: #84994F; color: white } """)
            buyButton.clicked.connect(lambda _, item=itemName: self.marketBuyItem(item))
            table.setCellWidget(row, 2, buyButton)
            
            sellButton = QPushButton("Sell")
            sellButton.setStyleSheet(""" QPushButton { background: #BF092F; color: white } """)
            sellButton.clicked.connect(lambda _, item=itemName: self.marketSellItem(item))
            table.setCellWidget(row, 3, sellButton)
            
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setColumnWidth(0, 93)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 100)
    
    def marketUpdatePrices(self):
        for item in self.items:
            if "🦞Crayfish" in item:
                base = 15 if "Red" in item else 25
                variation = random.randint(-3, 5)
                self.prices[item] = max(5, base + variation)
            
        self.marketTable()
    
    def marketBuyItem(self, itemName):
        price = self.prices[itemName]
        
        if self.essentials.money < price:
            self._marketShowMessage("Not Enough money!", "warning")
            return
        
        self.essentials.update("money", self.essentials.money - price)
        
        if itemName == "🦞Crayfish Red":
            self.essentials.update("crayFish_Red", self.essentials.crayFish_Red + 1)
        elif itemName == "🦞Crayfish Blue":
            self.essentials.update("crayFish_Blue", self.essentials.crayFish_Blue + 1)
        elif itemName == "🧪Booster":
            self.essentials.update("boosters", self.essentials.boosters + 1)
            
        self.essentials.update("total_Crayfish", self.essentials.crayFish_Red + self.essentials.crayFish_Blue)
        self._marketShowMessage(f"Bought 1: {itemName} for: {price} ₱", "info")
        self.markeToDashboardUpdate()
        
    def marketSellItem(self, itemName):
        price = self.prices[itemName]
        
        if itemName == "🦞Crayfish Red" and self.essentials.crayFish_Red > 0:
            self.essentials.update("crayFish_Red", self.essentials.crayFish_Red - 1)
        elif itemName == "🦞Crayfish Blue" and self.essentials.crayFish_Blue > 0:
            self.essentials.update("crayFish_Blue", self.essentials.crayFish_Blue - 1)
        elif itemName == "🧪Booster":
            if self.essentials.boosters > 0:
                self.essentials.update("boosters", self.essentials.boosters - 1)
            else: 
                self._marketShowMessage("You do not have any boosters to sell!", "warning")
                return
        else:
            self._marketShowMessage(f"You do not have any: {itemName} to sell!", "warning")
        
        self.essentials.update("money", self.essentials.money + price)    
        self.essentials.update("total_Crayfish", self.essentials.crayFish_Red + self.essentials.crayFish_Blue)
        self._marketShowMessage(f"Sold 1: {itemName} for: {price} ₱", "info")
        self.markeToDashboardUpdate()
        
    
    def markeToDashboardUpdate(self):
        self.ui.lineEdit_money.setText(str(self.essentials.money))
        self.ui.lineEdit_money_2.setText(str(self.essentials.totalCrayFish))
    
    def _marketCreateTableItem(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() ^ 2)
        return item
    
    def _marketShowMessage(self, text, msgType):
        msg = QMessageBox()
        msg.setWindowTitle("Market Notification")
        msg.setText(text)
        if msgType == "warning":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)
        msg.exec_()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Market()
    window.show()
    sys.exit(app.exec_())