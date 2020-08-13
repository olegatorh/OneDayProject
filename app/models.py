from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"(id: {self.id}, username: {self.username}, email: {self.email})"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.Column(db.String(20), nullable=False, default="stranger")
    bord_id = db.Column(db.String, db.ForeignKey("borda.bord_name"))

    def __repr__(self):
        return f'(id:{self.id}, author: {self.author},' \
               f' bord_id: {self.bord_id}, body: {self.body}, time: {self.timestamp})'


class Borda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    bord_name = db.Column(db.String(128), index=True, unique=True)
    creator_name = db.Column(db.String(20), index=True, nullable=False, default="stranger")

    def __repr__(self):
        return f"(bord_name: {self.bord_name}, time: {self.timestamp})"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
