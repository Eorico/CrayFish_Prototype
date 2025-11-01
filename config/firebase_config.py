import pyrebase

fireBaseConfig = {
    "apiKey": "AIzaSyCq-b0o_-doU1h9CO5YYrMmysAIDNJU9S8",
    "authDomain": "farmcrayfish.firebaseapp.com",
    "databaseURL": "https://farmcrayfish-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "farmcrayfish",
    "storageBucket": "farmcrayfish.appspot.com",
    "messagingSenderId": "549511847617",
    "appId": "1:549511847617:web:4c4ba76c2269844c303e40",
    "measurementId": "G-54D63Y5DQP"
}

firebase = pyrebase.initialize_app(fireBaseConfig)
auth = firebase.auth()
db = firebase.database()