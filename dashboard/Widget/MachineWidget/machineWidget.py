from dashboard.Logic.AbstractMethods.WidgetAbs import OpenWidgetBtn

class MachineWidget(OpenWidgetBtn):
    def __init__(self, ml):
        super().__init__()
        self.ml = ml
        
    def OpenWindow(self):
        self.ml.show()