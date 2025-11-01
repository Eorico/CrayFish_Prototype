from Designer_Files.ui.authentication_ui import Ui_MainWindow as UI_MAIN
from auth.login import *
from controller.auth_controller import AuthController as AUTH_CON
from PyQt5.QtCore import QTimer as timer

class SignUp:
    def __init__(self, ui:UI_MAIN):
        self.ui = ui
        self.auth = AUTH_CON()
        self.login = Login(self.ui)
        
        self.isSignUp = False
        
        self.ui.lineEdit_SIGNUP_NAME.setFocus()
        
        self.ui.lineEdit_SIGNUP_NAME.returnPressed.connect(self.focusEmail)
        self.ui.lineEdit_SIGNUP_EMAIL.returnPressed.connect(self.focusPassword)
        self.ui.lineEdit_2_SIGNUPPASSWORD.returnPressed.connect(self.focusconfirmPassword)
        self.ui.lineEdit_2_CONFIRM_PASSWORD.returnPressed.connect(self.createAcc)
        
    def focusEmail(self):
        self.ui.lineEdit_SIGNUP_EMAIL.setFocus()
        
    def focusPassword(self):
        self.ui.lineEdit_2_SIGNUPPASSWORD.setFocus()
        
    def focusconfirmPassword(self):
        self.ui.lineEdit_2_CONFIRM_PASSWORD.setFocus()
        
    def SignUpPage(self):
        self.ui.AuthenticationPages.setCurrentIndex(1)
        self.ui.lineEdit_SIGNUP_NAME.setFocus()
        
    def resetSignUpBtn(self):
        self.isSignUp = False
        self.ui.SIGNUP_BTN.setEnabled(True)
        
    def createAcc(self):
        if self.isSignUp:
            return
        self.isSignUp = True
        self.ui.SIGNUP_BTN.setEnabled(False)
        
        username = self.ui.lineEdit_SIGNUP_NAME.text()
        email = self.ui.lineEdit_SIGNUP_EMAIL.text()
        password = self.ui.lineEdit_2_SIGNUPPASSWORD.text()
        confirmpassword = self.ui.lineEdit_2_CONFIRM_PASSWORD.text()

        if password != confirmpassword:
            self.ui.label_validation_signup.setText("Passwords do not match")
            self.ui.label_validation_signup.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_signup.setText(""))
            self.resetSignUpBtn()
            return
        
        elif not username:
            self.ui.label_validation_signup.setText("Please enter a name!")
            self.ui.label_validation_signup.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_signup.setText(""))
            self.resetSignUpBtn()
            return

        success, message = self.auth.signUp(username, email, password, confirmpassword)
        if success:
            self.ui.label_validation_signup.setText("Sign up successful!")
            self.ui.label_validation_signup.setStyleSheet("""color: green;""")
            timer.singleShot(2000, lambda: (
                self.ui.label_validation_signup.setText(""),
                self.login.LoginPage()
            ))
        else:
            self.ui.label_validation_signup.setText(f"Sign up failed: {message}")
            self.ui.label_validation_signup.setStyleSheet("""color: red;""")
            timer.singleShot(2000, lambda: self.ui.label_validation_signup.setText(""))
            self.resetSignUpBtn()
            
    def SignUp_Con_Google(self):
        self.ui.label_validation_login.setText("Coming Soon...:)")
        self.ui.label_validation_login.setStyleSheet("""color: blue;""")
        timer.singleShot(2000, lambda: (self.ui.label_validation_login.setText("")))