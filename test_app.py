"""Tests of the views of the Setlist Manager app."""

import os
from unittest import TestCase
from models import db, Song, Setlist, SetlistSong, User

os.environ["DATABASE_URL"] = "postgresql:///setlist-manager-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False
app.config["DEBUG_TB_ENABLED"] = False


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

        self.uid_1 = self.test_user_1.id
        self.uid_2 = self.test_user_2.id

        self.song_a = Song(
            user_id=self.uid_1,
            title="Song A",
            artist="Artist 1",
        )
        self.song_b = Song(
            user_id=self.uid_2,
            title="Song B",
            artist="Artist 2",
        )
        self.song_c = Song(
            user_id=self.uid_1,
            title="Song C",
            artist="Artist 3",
        )

        self.lyrics_test_song = Song(
            user_id=self.uid_1,
            title="Never Gonna Give You Up",
            artist="Rick Astley",
        )

        self.test_setlist = Setlist(user_id=self.uid_1, name="Test Setlist 1")

        db.session.add(self.song_a)
        db.session.add(self.song_b)
        db.session.add(self.song_c)
        db.session.add(self.lyrics_test_song)
        db.session.add(self.test_setlist)
        db.session.commit()

        self.lyrics_song_id = self.lyrics_test_song.id

        self.setlist_id = self.test_setlist.id

        setlist_song_0 = SetlistSong(
            setlist_id=self.setlist_id, song_id=self.song_b.id, index=0
        )
        setlist_song_1 = SetlistSong(
            setlist_id=self.setlist_id, song_id=self.song_a.id, index=1
        )

        setlist_song_2 = SetlistSong(
            setlist_id=self.setlist_id, song_id=self.song_c.id, index=2
        )

        self.test_setlist.setlist_songs.append(setlist_song_0)
        self.test_setlist.setlist_songs.append(setlist_song_1)
        self.test_setlist.setlist_songs.append(setlist_song_2)

        db.session.add(self.test_setlist)
        db.session.commit()

    def tearDown(self):
        """Resets the test environment after every test."""

        db.session.rollback()

    def test_show_homepage_not_logged_in(self):
        """Ensures the not-logged-in homepage is shown when not logged in"""

        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("To continue, please do one of the following:", html)

    def test_show_homepage_logged_in(self):
        """Ensures the logged-in homepage is shown when logged in."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome back, user1!", html)

    def test_sign_up(self):
        """Ensures a user is created when the sign-up route is followed"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                if sess.get(CURR_USER_KEY):
                    del sess[CURR_USER_KEY]

            resp = client.post(
                "/sign-up",
                data={
                    "username": "newuser",
                    "password": "testpassword",
                    "email": "newuser@domain.tld",
                },
            )

            user = User.query.filter_by(email="newuser@domain.tld").first()

            self.assertEqual(user.username, "newuser")

    def test_log_in(self):
        """Verifies log-in functionality"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                if sess.get(CURR_USER_KEY):
                    del sess[CURR_USER_KEY]

            resp = client.post(
                "/log-in",
                data={
                    "username": "user1",
                    "password": "password1",
                },
            )
            html = resp.get_data(as_text=True)

            self.assertIn("user1", html)

    def test_log_out(self):
        """Verifies log-out functionality"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post("/log-out", data={})
            html = resp.get_data(as_text=True)

            self.assertNotIn("user1", html)

    def test_show_all_setlists(self):
        """Ensures all setlists can be viewed"""

        with app.test_client() as client:
            resp = client.get("/setlists")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Setlist Manager: All Setlists", html)
            self.assertIn("Test Setlist 1", html)

    def test_show_all_songs(self):
        """Ensures all songs can be viewed"""

        with app.test_client() as client:
            resp = client.get("/songs")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Setlist Manager: All Songs", html)
            self.assertIn("Song B", html)

    def test_show_current_user(self):
        """Ensures logged-in user page is viewable, with update link"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get(f"/users/{self.uid_1}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("User: user1", html)
            self.assertIn("Update Preferences", html)

    def test_show_other_user(self):
        """Ensures not-logged-in user is viewable, without update link"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get(f"/users/{self.uid_2}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("User: user2", html)
            self.assertNotIn("Update Preferences", html)

    def test_show_user_setlists(self):
        """Ensures all a logged-in user's setlists are viewable"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get("/your-setlists")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("user1's Setlists", html)
            self.assertIn("Test Setlist 1", html)

    def test_show_user_songs(self):
        """Ensures all a logged-in user's songs are viewable"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get("/your-songs")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("user1's Songs", html)
            self.assertIn("Song A", html)
            self.assertNotIn("Song B", html)
            self.assertIn("Song C", html)

    def test_add_song(self):
        """Ensures a user can add a song"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                "/songs/new",
                data={
                    "title": "Test Song 123",
                    "artist": "Fake Artist",
                },
            )

            song = Song.query.filter_by(title="Test Song 123").first()

            self.assertEqual(song.artist, "Fake Artist")
            self.assertEqual(song.user_id, self.uid_1)

    def test_add_setlist(self):
        """Ensures a user can add a setlist"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                "/setlists/new",
                data={
                    "name": "New Setlist ABC",
                },
            )

            setlist = Setlist.query.filter_by(name="New Setlist ABC").first()

            self.assertEqual(setlist.user_id, self.uid_1)

    def test_update_setlist(self):
        """Ensures the setlist update internal api route functions"""

        new_order = [self.song_c.id, self.song_a.id, self.song_b.id]

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            data = {"songs": new_order}

            resp = client.post(
                f"/api/setlists/{self.setlist_id}/update-songs",
                json=data,
            )

            setlist = Setlist.query.get(self.setlist_id)

            self.assertEqual(setlist.songs[0].id, new_order[0])
            self.assertEqual(setlist.songs[1].id, new_order[1])
            self.assertEqual(setlist.songs[2].id, new_order[2])

    def test_update_song(self):
        """Ensures functionality of updating a song's basic information"""

        song_id = self.song_a.id

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                f"/songs/{song_id}/update",
                data={
                    "title": "New Title",
                    "artist": "New Artist",
                    "lyrics": "New Lyrics",
                },
            )

            song = Song.query.get(song_id)

            self.assertEqual(song.title, "New Title")
            self.assertEqual(song.artist, "New Artist")
            self.assertEqual(song.lyrics, "New Lyrics")

    def test_import_lyrics(self):
        """Makes sure lyrics can be fetched"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.get(
                f"/songs/{self.lyrics_song_id}/fetch-lyrics", follow_redirects=True
            )
            html = resp.get_data(as_text=True)

            self.assertIn("Never gonna give you up", html)
            self.assertIn("Never gonna let you down", html)
            self.assertIn("Never gonna run around", html)
            self.assertIn("And desert you", html)

    def test_update_user(self):
        """Ensures functionality of updating user information"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                "/users/update",
                data={
                    "username": "New Username",
                    "email": "newaddress@email.com",
                    "pwd": "password1",
                },
            )

            user = User.query.get(self.uid_1)

            self.assertEqual(user.username, "New Username")
            self.assertEqual(user.email, "newaddress@email.com")

    def test_del_user(self):
        """Ensures a user can delete their own account"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1
            resp = client.post(
                f"/users/{self.uid_1}/delete", data={}, follow_redirects=True
            )
            html = resp.get_data(as_text=True)

            self.assertIn("User deleted successfully!", html)
            self.assertEqual(resp.status_code, 200)

    def test_del_song(self):
        """Ensures a user can delete their own song"""

        song_id = self.song_a.id

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                f"/songs/{song_id}/delete", data={}, follow_redirects=True
            )
            html = resp.get_data(as_text=True)

            self.assertIn("Song deleted successfully!", html)
            self.assertIn("user1's Songs", html)
            self.assertNotIn("Song A", html)

    def test_del_setlist(self):
        """Ensures a user can delete their own setlist"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid_1

            resp = client.post(
                f"/setlists/{self.setlist_id}/delete", data={}, follow_redirects=True
            )
            html = resp.get_data(as_text=True)

            self.assertIn("Setlist deleted successfully!", html)
            self.assertIn("user1's Setlists", html)
            self.assertNotIn("Test Setlist 1", html)

    def test_perform(self):
        """Verifies performance mode functionality"""

        first_song = self.song_b.id

        with app.test_client() as client:

            resp = client.get(f"/setlists/{self.setlist_id}/perform/{first_song}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Perform: Test Setlist 1", html)
            self.assertIn("Song B", html)
            self.assertIn("(by Artist 2)", html)
