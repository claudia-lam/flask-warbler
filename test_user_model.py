"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)


class FollowsTestCase(UserModelTestCase):

    def test_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1_follows_u2 = Follows(
            user_being_followed_id=self.u2_id,
            user_following_id=self.u1_id)

        db.session.add(u1_follows_u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))

    def test_is_not_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_following(u2))

    def test_is_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1_follows_u2 = Follows(
            user_being_followed_id=self.u2_id,
            user_following_id=self.u1_id)

        db.session.add(u1_follows_u2)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))

    def test_is_not_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u2.is_followed_by(u1))


class UserAuthenticateTestCase(UserModelTestCase):

    def test_signup_success(self):
        User.signup("u3", "u3@email.com", "password", None)

        self.assertIsNotNone(User.query.filter(User.username == "u3").first())

    def test_signup_fail(self):
        user = User.signup("u3", "u3@email.com", None)

        self.assertIsNone(user)
