"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Follows, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
# db.drop_all()
db.create_all() 

# u = User(
#             id= 1,
#             email="test@test.com",
#             username="testuser",
#             password="HASHED_PASSWORD"
#         )
# u2 = User(
#             id= 2,
#             email="test2@test.com",
#             username="testuser2",
#             password="HASHED_PASSWORD"
#         )

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        

        self.client = app.test_client()
    
    # def tearDown(self):
    #     """Delete tables after test"""
    #     db.session.remove()
    #     db.session.commit()
    #     # db.drop_all()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does __repr__ method return correctly? """
        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(repr(u), '<User #1: testuser, test@test.com>')

    def test_is_following(self):
        """Does is_following detect user1 following user2?"""

        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            id= 2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.add(u2)


        u.following.append(u2)
   

        self.assertIn(u2, u.following) 
    
    def test_is_not_following(self):
        """ Does is_following detect user1 NOT following user2?"""
        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            id= 2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        self.assertNotIn(u2.id, u.following)

    def test_is_followed_by(self):
        """Does is_followed_by detect user1 followed by user2?"""
        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            id= 2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.add(u2)
        u2.following.append(u)
        db.session.commit()

        self.assertIn(u2, u.followers)

    def test_is_not_followed_by(self):
        """Does is_followed_by detect user1 not followed by user2?"""
        u = User(
            id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            id= 2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        self.assertNotIn(u2.id, u.followers)
    
    def test_create_user(self):
        """Does user.create return a user when given valid credentials?"""
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )
        self.assertIsInstance(user, User)
    def test_create_user_fail(self):
        """ Does user.create fail if given non-valid credentials?"""

        user = User.signup(
            email="bademail",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="image_url"
        )

        self.assertIsNot(user, User)

    def test_user_authenticate(self):
        """Does user.authenticate return a user when given valid username and pass?"""
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
            )
        
        user_auth = User.authenticate(username="testuser", password="HASHED_PASSWORD")
        
        self.assertIsInstance(user_auth, User)
    def test_user_authenticate_fail_username(self):
        """Does user.authenticate fail with an invalid username?"""
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
            )
        
        user_auth = User.authenticate(username="wrong_username", password="HASHED_PASSWORD")
        
        self.assertIsNot(user_auth, User)

    def test_user_authenticate_fail_password(self):
        """Does user.authenticate fail with an invalid password?"""
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
            )
        
        user_auth = User.authenticate(username="testuser", password="wrong_password")
        
        self.assertIsNot(user_auth, User)