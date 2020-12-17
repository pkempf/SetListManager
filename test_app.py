"""Tests of the views of the Setlist Manager app."""

import os
from unittest import TestCase
from models import db, connect_db, Song, Setlist, SetlistSong, User

os.environ["DABASE_URL"] = "postgresql://setlist-manager-test"

from app import app, CURR_USER_KEY, LYRICS_API_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class SetlistManagerViewTestCase(TestCase):
    """Tests for the app's views."""

    def setUp(self):
        """Create test client and add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.test_user_1 = User.signup("user1", "user1@test.com", "password1")
        self.test_user_2 = User.signup("user2", "user2@test.com", "password2")

        db.session.add(self.test_user_1)
        db.session.add(self.test_user_2)
        db.session.commit()

        self.song_a = Song(
            user_id=self.test_user_1.id, title="Song A", artist="Artist 1"
        )
        self.song_b = Song(
            user_id=self.test_user_2.id, title="Song B", artist="Artist 2"
        )
        self.song_c = Song(
            user_id=self.test_user_1.id, title="Song C", artist="Artist 3"
        )

        self.test_setlist = Setlist(user_id=self.test_user_1.id, name="Test Setlist 1")

        db.session.add(self.song_a)
        db.session.add(self.song_b)
        db.session.add(self.song_c)
        db.session.add(self.test_setlist)
        db.session.commit()

        setlist_song_0 = SetlistSong(
            setlist_id=self.test_setlist.id, song_id=self.song_b.id, index=0
        )
        setlist_song_1 = SetlistSong(
            setlist_id=self.test_setlist.id, song_id=self.song_a.id, index=1
        )

        self.test_setlist.setlist_songs.append(setlist_song_0)
        self.test_setlist.setlist_songs.append(setlist_song_1)

        db.session.add(self.test_setlist)
        db.session.commit()

        self.setlist_id = self.test_setlist.id
