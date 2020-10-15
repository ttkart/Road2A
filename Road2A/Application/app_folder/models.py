from app_folder import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app_folder import login_manager
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """
        Creates the ID, username, email, and password_hash variables for each user. 
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')

@login_manager.user_loader
def load_user(user_id):
    """
        Takes in a user ID and returns that user's data.
    """
    return User.query.get(int(user_id))


class Appointments(db.Model):
    """
       Creates the variables for user appointments. 
    """
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(64))
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    time = db.Column(db.String(16))
 
    def __repr__(self):
        return '<Appointments: {}>'.format(self.body)


class Availability(UserMixin, db.Model):
    """
       Creates variable for user availability. 
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    time_Range = db.Column(db.String(128))
    meeting_Length = db.Column(db.String(128))