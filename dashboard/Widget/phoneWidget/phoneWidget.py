from dashboard.Logic.AbstractMethods.WidgetAbs import OpenWidgetBtn

class PhoneWidget(OpenWidgetBtn):  
    def __init__(self, phone):
        super().__init__()
        self.phone = phone
        
    def OpenWindow(self):
        self.phone.show()