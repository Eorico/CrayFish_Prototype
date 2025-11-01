from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication
from Designer_Files.ui.inventory_ui import Ui_Inventory as INV_UI
import sys

class Inventory(MAIN, INV_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Inventory()
    window.show()
    sys.exit(app.exec_())