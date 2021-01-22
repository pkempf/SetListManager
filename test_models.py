"""Tests of the models for the Setlist Manager app."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, Song, Setlist, SetlistSong, User

os.environ["DATABASE_URL"] = "postgresql:///setlist-manager-test"

from app import app

db.create_all()


class SetlistManagerModelTestCase(TestCase):
    """Tests for the app's models."""

    def setUp(self):
        """Create test client, add sample data."""

        users = User.query.all()
        for u in users:
            db.session.delete(u)
        SetlistSong.query.delete()
        Song.query.delete()
        Setlist.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Roll back the changes made in each test."""

        db.session.rollback()

    # User model ################################################

    def test_user_model(self):
        """Ensures the basic functionality of the user model."""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no songs or setlists, and user.darkmode should = f
        self.assertEqual(len(u.songs), 0)
        self.assertEqual(len(u.setlists), 0)
        self.assertEqual(u.darkmode, False)

    def test_user_repr(self):
        """Does the User model's __repr__ return what it should?"""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: testuser, testuser@email.com>")

    def test_create_invalid_user(self):
        """Does User.create throw an error when given insufficient credentials?"""

        u = User(username="testuser", email="testuser@email.com")

        integrity_error_thrown = False

        try:
            db.session.add(u)
            db.session.commit()
        except IntegrityError:
            integrity_error_thrown = True

        self.assertTrue(integrity_error_thrown)

    def test_authenticate_username_valid(self):
        """Does User.authenticate_username work with valid credentials?"""

        u = User.signup(
            username="testuser", email="testuser@email.com", password="PASSWORD"
        )
        db.session.commit()

        logged_in_user = User.authenticate_username(
            username="testuser",
            password="PASSWORD",
        )

        self.assertEqual(u, logged_in_user)

    def test_authenticate_username_invalid(self):
        """Does User.authenticate_username fail with a bad password?"""

        u = User.signup(
            username="testuser", email="testuser@email.com", password="PASSWORD"
        )
        db.session.commit()

        logged_in_user = User.authenticate_username(
            username="testuser",
            password="WRONG_PASSWORD",
        )

        self.assertFalse(logged_in_user)

    def test_authenticate_email_valid(self):
        """Does User.authenticate_email work with valid credentials?"""

        u = User.signup(
            username="testuser", email="testuser@email.com", password="PASSWORD"
        )
        db.session.commit()

        logged_in_user = User.authenticate_email(
            email="testuser@email.com",
            password="PASSWORD",
        )

        self.assertEqual(u, logged_in_user)

    def test_authenticate_email_invalid(self):
        """Does User.authenticate_email fail with a bad password?"""

        u = User.signup(
            username="testuser", email="testuser@email.com", password="PASSWORD"
        )
        db.session.commit()

        logged_in_user = User.authenticate_email(
            email="testuser@email.com",
            password="WRONG_PASSWORD",
        )

        self.assertFalse(logged_in_user)

    # Song model ################################################

    def test_song_model(self):
        """Ensures the basic functionality of the song model."""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        s = Song(
            user_id=u.id, title="Song Title", artist="Test Artist", lyrics="Test Lyrics"
        )

        db.session.add(s)
        db.session.commit()

        self.assertEqual(s.user, u)
        self.assertEqual(s.title, "Song Title")
        self.assertEqual(s.artist, "Test Artist")
        self.assertEqual(s.lyrics, "Test Lyrics")

    def test_song_repr(self):
        """Does the Song model's __repr__ return what it should?"""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        s = Song(
            user_id=u.id, title="Song Title", artist="Test Artist", lyrics="Test Lyrics"
        )

        db.session.add(s)
        db.session.commit()

        self.assertEqual(repr(s), f"<Song {s.id}: Song Title by Test Artist>")

    # Setlist model #############################################

    def test_setlist_model(self):
        """Ensures the basic functionality of the Setlist model."""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        sl = Setlist(user_id=u.id, name="Test Setlist", notes="Test Notes")

        db.session.add(sl)
        db.session.commit()

        self.assertEqual(sl.user_id, u.id)
        self.assertEqual(sl.name, "Test Setlist")
        self.assertEqual(sl.notes, "Test Notes")
        self.assertEqual(len(sl.songs), 0)
        self.assertEqual(len(sl.setlist_songs), 0)

    # SetlistSong model #########################################

    def test_setlist_song_model(self):
        """Ensures the basic functionality of the SetlistSong model."""

        u = User(
            username="testuser", email="testuser@email.com", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        s = Song(
            user_id=u.id, title="Song Title", artist="Test Artist", lyrics="Test Lyrics"
        )

        db.session.add(s)
        db.session.commit()

        sl = Setlist(user_id=u.id, name="Test Setlist", notes="Test Notes")

        db.session.add(sl)
        db.session.commit()

        ss = SetlistSong(setlist_id=sl.id, song_id=s.id, index=0)

        db.session.add(ss)
        db.session.commit()

        self.assertEqual(ss.index, 0)
        self.assertEqual(ss.setlist_id, sl.id)
        self.assertEqual(ss.song_id, s.id)

        self.assertEqual(len(sl.songs), 1)
        self.assertEqual(len(sl.setlist_songs), 1)
        self.assertEqual(sl.setlist_songs[0].id, ss.id)
