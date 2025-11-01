from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication, QTableWidgetItem, QPushButton
from PyQt5.QtCore import QTimer as timer, pyqtSignal
from PyQt5.QtGui import QColor as color

from Designer_Files.ui.phone_ui import Ui_Phone as PHONE_UI
from dashboard.Logic.Water.waterLogic import WaterLogic
from dashboard.Logic.Temperature.temperature import Temperature
from datetime import datetime
import sys 

class Phone(MAIN, PHONE_UI):
    newPhoneNotif = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.waterLogic = WaterLogic(self)
        self.temperature = Temperature(self)
        
        self.tableWidget_phone.setColumnWidth(0, 80)
        self.tableWidget_phone.setColumnWidth(1, 160)
        self.tableWidget_phone.setColumnWidth(2, 60)
        
    def phoneDeleteRow(self, row):
        self.tableWidget_phone.removeRow(row)
        
    def notify(self, message):
        rowPosition = self.tableWidget_phone.rowCount()
        self.tableWidget_phone.insertRow(rowPosition)
        
        timeNow = datetime.now().strftime("%H:%M:%S")
        self.tableWidget_phone.setItem(rowPosition, 0, QTableWidgetItem(timeNow))
        self.tableWidget_phone.setItem(rowPosition, 1, QTableWidgetItem(message))
        
        deleteBtn = QPushButton("Delete")
        deleteBtn.setStyleSheet("""QPushButton {background-color: red;} """)
        deleteBtn.clicked.connect(lambda _, r=rowPosition: self.phoneDeleteRow(r))
        self.tableWidget_phone.setCellWidget(rowPosition, 2, deleteBtn)
        
        self.newPhoneNotif.emit()
        
        hgLightColor = color(255, 255, 200)
        defaultColor = color(255, 255, 255)
        
        def blink(times=3):
            if times == 0:
                self.tableWidget_phone.item(rowPosition, 1).setBackground(defaultColor)
                return
            currentColor = (hgLightColor if times % 2 == 0 else defaultColor)
            for col in range(2):
                item = self.tableWidget_phone.item(rowPosition, col)
                if item:
                    item.setBackground(currentColor)
            timer.singleShot(200, lambda: blink(times - 1))
            
        blink()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Phone()
    window.show()
    sys.exit(app.exec_())