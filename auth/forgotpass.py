from Designer_Files.ui.authentication_ui import Ui_MainWindow as UI_MAIN
from controller.auth_controller import AuthController as AUTH_CON
from PyQt5.QtCore import QTimer as timer

class ForgotPassword:
    def __init__(self, ui: UI_MAIN):
        self.ui = ui
        self.auth = AUTH_CON()
        
        self.isForgetPass = False
        
        self.ui.lineEdit_EMAIL_FORGET.setFocus()
    
    def ForgetPassPage(self):
        self.ui.AuthenticationPages.setCurrentIndex(2)
        self.ui.lineEdit_EMAIL_FORGET.setFocus()
        
    def resetForgetPassBtn(self):
        self.isForgetPass = False
        self.ui.SUBMIT_FORGET_BTN.setEnabled(True)

    def resetPass(self):
        
        if self.isForgetPass:
            return
        self.isForgetPass = True
        self.ui.SUBMIT_FORGET_BTN.setEnabled(False)
        
        email = self.ui.lineEdit_EMAIL_FORGET.text()
        success, message = self.auth.forgotPassword(email)
        if success:
            self.ui.label_validation_forget_pass.setText("Reset link sent to your email!")
            self.ui.label_validation_forget_pass.setStyleSheet("""color: green;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_forget_pass.setText(""))
        else:
            self.ui.label_validation_forget_pass.setText(f"Error: {message}")
            self.ui.label_validation_forget_pass.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_forget_pass.setText(""))
            self.resetForgetPassBtn()