from Designer_Files.ui.authentication_ui import Ui_MainWindow as UI_MAIN
from PyQt5.QtCore import QTimer as timer
from controller.auth_controller import AuthController as AUTH_CON
from dashboard.Dashboard.dashboard import DashboardWindow

class GoDashboard:
    def Dashboard(self, username, ui, email, idToken):
        self.dashboard = DashboardWindow(username=username, email=email, idToken=idToken)
        self.dashboard.show()
        ui.close()
        
class Login:
    def __init__(self, ui:UI_MAIN):
        
        self.ui = ui
        self.auth = AUTH_CON()
        
        self.isLogIn = False
        
        self.goDashboard = GoDashboard()
        
        self.ui.lineEdit_EMAIL.setFocus()
        self.ui.lineEdit_EMAIL.returnPressed.connect(self.focusPass)
        self.ui.lineEdit_2_PASSWORD_BTN.returnPressed.connect(self.loginUser)
    
    def focusPass(self):
        self.ui.lineEdit_2_PASSWORD_BTN.setFocus()
    
    def LoginPage(self):
        self.ui.lineEdit_EMAIL.setFocus()
        self.ui.AuthenticationPages.setCurrentIndex(0)
        
    def resetLogBtn(self):
        self.isLogIn = False
        self.ui.LOGIN_BTN.setEnabled(True)
        
    def loginUser(self):
        
        if self.isLogIn:
            return
        self.isLogIn = True
        self.ui.LOGIN_BTN.setEnabled(False)
        
        email = self.ui.lineEdit_EMAIL.text()
        password = self.ui.lineEdit_2_PASSWORD_BTN.text()

        if not email:
            self.ui.label_validation_email.setText("Please enter an email")
            self.ui.label_validation_email.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_email.setText(""))
            self.resetLogBtn()
            return
        elif not password:
            self.ui.label_validation_pass.setText("Please enter a password")
            self.ui.label_validation_pass.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_pass.setText(""))
            self.resetLogBtn()
            return

        success, message = self.auth.login(email, password)
        if success:
            import pyrebase
            from config.firebase_config import fireBaseConfig as config
            
            firebase = pyrebase.initialize_app(config)
            auth = firebase.auth()
            user = auth.sign_in_with_email_and_password(email, password)
            idToken = user['idToken']
            
            username = self.auth.getUsername()
            self.ui.label_validation_login.setText("Login successful!")
            self.ui.label_validation_login.setStyleSheet("""color: green;""")
            timer.singleShot(2000, lambda: (
                self.ui.label_validation_login.setText(""),
                self.goDashboard.Dashboard(username, self.ui, email, idToken)
            ))
        else:
            self.ui.label_validation_login.setText(f"Login failed: {message}")
            self.ui.label_validation_login.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_login.setText(""))
            self.resetLogBtn()