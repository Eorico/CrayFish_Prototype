from dashboard.Logic.AbstractMethods.WidgetAbs import OpenWidgetBtn

class MarketWidget(OpenWidgetBtn):
    def __init__(self, market):
        super().__init__()
        self.market = market
    
    def OpenWindow(self):
        self.market.show()