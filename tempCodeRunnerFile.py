from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication
from Designer_Files.ui.authentication_ui import Ui_MainWindow as UI_MAIN
from auth.login import *
from auth.signup import *
from auth.forgotpass import *
import sys

class AuthWindow(MAIN, UI_MAIN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.login = Login(self)
        self.signUp = SignUp(self)
        self.forgetpass = ForgotPassword(self)
        
        self.lineEdit_EMAIL.setFocus()

        self.LOGIN_BTN.clicked.connect(self.login.loginUser)
        self.SIGNUP.clicked.connect(self.signUp.SignUpPage)
        self.SIGNUP_BTN.clicked.connect(self.signUp.createAcc)
        self.FORGOTPASSWORD.clicked.connect(self.forgetpass.ForgetPassPage)
        self.SUBMIT_FORGET_BTN.clicked.connect(self.forgetpass.resetPass)
        self.BACKTOLOGIN1.clicked.connect(self.login.LoginPage)
        self.BACKTOLOGIN2.clicked.connect(self.login.LoginPage)
        self.G_LOGIN_CONTINUE_BTN.clicked.connect(self.signUp.SignUp_Con_Google)
        
        print("Login Opening...")

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())