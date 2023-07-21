"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u1.bio = "test_bio"
        u1.location = "test_location"
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()


class UserViewTestCase(UserBaseViewTestCase):
    def test_logout(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/logout", follow_redirects=True)
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("signup", html)

            # check if user can access followers page
            resp_anon = c.get(
                f"/users/{self.u1_id}/following", follow_redirects=True)
            html_anon = resp_anon.text

            self.assertEqual(resp_anon.status_code, 200)
            self.assertIn("signup", html_anon)

    def test_show_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")
            html = resp.text

            self.assertIn("test_bio", html)
            self.assertIn("test_location", html)

    def test_show_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")
            html = resp.text

            self.assertIn("test_bio", html)

    def test_show_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")
            html = resp.text

            self.assertIn("test_bio", html)

    def test_list_users(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users")
            html = resp.text

            self.assertIn("test_bio", html)

    def test_profile(self):
        with self.client as c:

            # authorized user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post('/users/profile', data={
                "username": "updated_username",
                "bio": "updated_bio",
                "password": "password"
            }, follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("updated_username", html)
            self.assertIn("updated_bio", html)

    def test_profile_wrong_password(self):
        with self.client as c:

            # wrong password
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(
                "/users/profile",
                data={
                    "username": "updatedU",
                    "password": "wrongpassword"
                },
                follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Wrong password. Try again.", html)

        # # unauthorized user
        # resp = c.post('/users/profile', data={
        #     "username": "updated_username",
        #     "bio": "updated_bio"
        # }, follow_redirects=False)

        # self.assertEquals(resp.status_code, 302)
        # self.assertEqual(resp.location, "/")
