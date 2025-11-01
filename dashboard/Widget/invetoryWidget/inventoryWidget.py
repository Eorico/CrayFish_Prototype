from dashboard.Logic.AbstractMethods.WidgetAbs import OpenWidgetBtn

class InventoryWidget(OpenWidgetBtn):
    def __init__(self, inv):
        super().__init__()
        self.inv = inv
        
    def OpenWindow(self):
        self.inv.show()
        