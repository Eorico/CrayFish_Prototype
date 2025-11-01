import pyrebase
from config.firebase_config import fireBaseConfig as config

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

class AuthController:
    def __init__(self):
        self.currentUser = None
    
    def getUsername(self):
        return self.currentUser
    
    def signUp(self, username, email, password, confirmpassword):
        try:
            # Check for Gmail domain
            if not email.lower().endswith("@gmail.com"):
                return False, "must end with @gmail.com"
                
            elif password != confirmpassword:
                return False, "Passwords do not match"
            
            elif len(password) < 8:
                return False, "8 characters is a must!"
            
            user = auth.create_user_with_email_and_password(email, password)
            
            signInUser = auth.sign_in_with_email_and_password(email, password)
            
            auth.update_profile(signInUser['idToken'], display_name=username)
            
            self.currentUser = username
            
            print(f"Account Created: {self.currentUser}")
            return True, "Account created successfully"
        except Exception as err:
            print(f"Sign up failed: {err}")
            return False, f"Sign-up failed"
        
    def login(self, email, password):
        try:
            # Check for Gmail domain
            if not email.lower().endswith("@gmail.com"):
                return False, "must end with @gmail.com"
            
            user = auth.sign_in_with_email_and_password(email, password)
            
            accountInfo = auth.get_account_info(user['idToken'])
            
            self.currentUser = accountInfo['users'][0].get('displayName', email)
            
            print(f"Login Successfull: {self.currentUser}")
            return True, "Login successfull" 
        except Exception as err:
            print(f"Login failed: {err}")
            return False, f"Login failed"
        
    def forgotPassword(self, email):
        try:
            # Check for Gmail domain
            if not email.lower().endswith("@gmail.com"):
                return False, "must end with @gmail.com"
            
            auth.send_password_reset_email(email)
            print("Reset Sent")
            return True, "Password reset email sent"
        except Exception as err:
            print(f"{err}")
            return False, f"Failed to sent"