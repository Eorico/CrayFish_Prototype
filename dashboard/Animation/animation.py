from PyQt5.QtCore import QTimer as timer
from Designer_Files.ui.dashboard_ui import Ui_MainWindow as DASH_MAIN 
from PyQt5.QtGui import QMovie, QTransform

class CrayFishAnimation:
    def __init__(self, ui: DASH_MAIN):
        self.ui = ui
        
    def initCrayfish(self):
        
        self.blueCraymovie_1 = QMovie("Designer_Files/assets/Crayfish_Blue_Move.gif") 
        self.ui.Blue_Cray1.setMovie(self.blueCraymovie_1)
        self.blueCraymovie_1.start()
        
        self.blueCraymovie_2 = QMovie("Designer_Files/assets/Crayfish_Blue_Move.gif")
        self.ui.Blue_Cray2.setMovie(self.blueCraymovie_2)
        self.blueCraymovie_2.start()
        
        self.redCraymovie_1 = QMovie("Designer_Files/assets/Crayfish_Red_Move.gif")
        self.ui.Red_Cray1.setMovie(self.redCraymovie_1)
        self.redCraymovie_1.start()
        
        self.redCraymovie_2 = QMovie("Designer_Files/assets/Crayfish_Red_Move.gif")
        self.ui.Red_Cray2.setMovie(self.redCraymovie_2)
        self.redCraymovie_2.start()
        
        self.dir = {
            self.ui.Blue_Cray1: 1,
            self.ui.Blue_Cray2: -1,
            self.ui.Red_Cray1: 1,
            self.ui.Red_Cray2: -1,
        } 
        
        self.flipped = {
            self.ui.Blue_Cray1: False,
            self.ui.Blue_Cray2: False,
            self.ui.Red_Cray1: False,
            self.ui.Red_Cray2: False,
        }
        
        self.moveTimer = timer(self.ui)
        self.moveTimer.timeout.connect(self.moveCrayFish)
        self.moveTimer.start(30)
        
    def moveCrayFish(self):
        crayFishes = [self.ui.Blue_Cray1, self.ui.Blue_Cray2, self.ui.Red_Cray1, self.ui.Red_Cray2]
        
        for cray in crayFishes:
            x = cray.x()
            y = cray.y()
            
            direction = self.dir[cray]
            x += 2 * direction
            cray.move(x, y)
            
            if x <= 0 and direction == -1:
                self.dir[cray] = 1
                if self.flipped[cray]:
                    self.FlipGIF(cray, False)
                    self.flipped[cray] = True
                    
            elif x + cray.width() >= self.ui.width() and direction == 1:
                self.dir[cray] = -1
                if not self.flipped[cray]:
                    self.FlipGIF(cray, True)
                    self.flipped[cray] = True
                
    def FlipGIF(self, label, flip):
        movie = label.movie()
        if not movie:
            return

        def update_frame():
            current_pixmap = movie.currentPixmap()
            if flip:
                flipped = current_pixmap.transformed(QTransform().scale(-1, 1))
                label.setPixmap(flipped)
            else:
                label.setPixmap(current_pixmap)

        movie.frameChanged.connect(update_frame)
        
    def stopAnimation(self):
        if hasattr(self, "moveTimer") and self.moveTimer.isActive():
            self.moveTimer.stop()
            print("Movement timer stopped")
            
        for moveAttr in [
            "blueCraymovie_1", "blueCraymovie_2",
            "redCraymovie_1", "redCraymovie_2"
        ]:
            movie = getattr(self, moveAttr, None)
            if movie and movie.state() == QMovie.Running:
                movie.stop()
                print(f"{moveAttr} animation stopped.")
                
        print("Crayfish stopped")