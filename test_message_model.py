import os
from unittest import TestCase
from models import db, Message, Likes, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test message model"""

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        u = User(
                id= 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        u2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u2)
        db.session.commit()

    
    def test_message_model(self):
        """Does the basic model work??"""
        u = User.query.get_or_404(1)

        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 1
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(u.messages), 1)

    def test_repr(self):
        """Does the __repr__ method return correctly?"""
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 1
        )

        self.assertEqual(repr(m), '<Message #1: Example Text, None>')
    
    def test_create_message(self):
        """Does create message succeed when given valid information?"""
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 1
        )
        self.assertIsInstance(m, Message)

    def test_create_message_fail(self):
        """Does create message fail when given invalid info? """
        m = Message(
            id= "This should be an integer",
            text= False,
            user_id= "This should also be an integer"

        )
        self.assertIsNot(m, Message)

    def test_user_messages(self):
        """Does message connect to user?"""
        u = User.query.get_or_404(1)
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 1
        )
        db.session.add(m)
        db.session.commit()

        self.assertIn(m, u.messages)
    
    def test_not_user_messages(self):
        """Does message connect to the wrong user?"""
        u = User.query.get_or_404(1)
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        db.session.add(m)
        db.session.commit()

        self.assertNotIn(m, u.messages)


    def test_user_likes(self):
        """Does the user detect liked message by user2?"""
        u = User.query.get_or_404(1)

        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        u.likes.append(m)

        self.assertIn(m, u.likes)

    def test_user_not_like(self):
        """Does the user detect lack of liked message by user2?"""
        u = User.query.get_or_404(1)

        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )

        self.assertNotIn(m, u.likes)
    
    # def test_message_likes(self):
    #     """Does the message detect users who have liked it?"""