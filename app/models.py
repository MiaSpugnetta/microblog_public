from app import app  #, db
from abstractions.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Package that implements password hashing (Flask dependency).
from flask_login import UserMixin  # As long as the required methods are implemented (is_authenticated, is_active, is_anonymous, get_id()), Flask_login  can work with user models that are based on any db system. UserMixin class includes generic implementations appropriate for most user model classes.
from app import login  # Keeps track of the logged in user by storing its unique identifier in Flask's user session (storage space assigned to each user who connects to the app). Flask-login needs app's help in loading a user. The extension expects that the app will configure a user loader function that can be calle to load a user given the ID.
from hashlib import md5
from time import time
import jwt


followers = db.Table('followers', db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):  # Inherits from db.Model, base class for all models from Flask-SQLAlchemy. It defines several fields as class variables. Fields are created as instances of the db.Column class, which takes the field type as an arguments (plus other optional args that make db searches efficient).
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # Method that defines how the object gets printed to the terminal. Useful for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)

    # Methods that allows a user object to do secure password verification, with no need to store the original password.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        # commented out when email not required
        #digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'http://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
#u = User(username='john', email='john@example.com')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
