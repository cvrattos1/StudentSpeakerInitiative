from flask_login import UserMixin

class studentAccount(UserMixin):
    
    def __init__(self, username):
        self.id = username


   