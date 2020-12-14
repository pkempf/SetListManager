"""Models for the Setlist Manager."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """A user of the Setlist Manager app."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    darkmode = db.Column(db.Boolean, nullable=False, default=False)

    songs = db.relationship("Song", backref="user")
    setlists = db.relationship("Setlist", backref="user")

    def __repr__(self):
        """Returns a representation of the user."""

        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def hash_password(cls, unhashed_password):
        """Hashes a password."""

        hashed_password = bcrypt.generate_password_hash(unhashed_password).decode(
            "UTF-8"
        )

        return hashed_password

    @classmethod
    def signup(cls, username, email, password):
        """Signs up a user; hashes password, adds user to system."""

        hashed_password = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)

        return user

    @classmethod
    def authenticate_username(cls, username, password):
        """Gets the user with that username/password, or returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_authenticated = bcrypt.check_password_hash(user.password, password)
            if is_authenticated:
                return user

        return False

    @classmethod
    def authenticate_email(cls, email, password):
        """Gets the user with that email/password, or returns False."""

        user = cls.query.filter_by(email=email).first()

        if user:
            is_authenticated = bcrypt.check_password_hash(user.password, password)
            if is_authenticated:
                return user


class Song(db.Model):
    """A song within the Setlist Manager app."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    lyrics = db.Column(db.Text, nullable=True)

    def serialize(self):
        """Returns a dictionary with the fields of the song, except the lyrics."""

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "artist": self.artist,
        }

    def __repr__(self):
        """Returns a string representation of the fields of the song."""
        return f"<Song {self.id}: {self.title} by {self.artist}>"


class Setlist(db.Model):
    """A setlist within the Setlist Manager app."""

    __tablename__ = "setlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.Text, nullable=False)

    notes = db.Column(db.Text, nullable=True)

    songs = db.relationship(
        "Song",
        order_by="SetlistSong.index",
        secondary="setlists_songs",
        backref="setlists",
    )
    setlist_songs = db.relationship("SetlistSong", backref="setlist")


class SetlistSong(db.Model):
    """Connection between a Setlist and a Song."""

    __tablename__ = "setlists_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setlist_id = db.Column(
        db.Integer, db.ForeignKey("setlists.id", ondelete="CASCADE"), nullable=False
    )
    song_id = db.Column(
        db.Integer, db.ForeignKey("songs.id", ondelete="CASCADE"), nullable=False
    )
    index = db.Column(db.Integer, nullable=False)

    # TODO: Add unique constraint - setlist_id + index


def connect_db(app):
    """Connects this database to the Flask app."""

    db.app = app
    db.init_app(app)