"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        exampleuser = User(
                id= 2,
            email="example@test.com",
            username="exampleuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(exampleuser)
      

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_add_message_other_user(self):
        """Can user add a message to another user's account?"""
        exampleuser = User.query.get_or_404(2)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello", "user":"exampleuser", "user_id": "2"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # self.assertEqual(resp.request.path, '/messages/new')

            # Message was not added to other user
            self.assertEqual(len(exampleuser.messages), 0)

    def test_show_message(self):
        """Show a message?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        db.session.add(m)
        db.session.commit()

        response = c.get("/messages/1")

        self.assertEqual(response.status_code, 200)

        message = Message.query.one()
        self.assertEqual(message.text,"Example Text")

    def test_delete_message_success(self):
        """ Delete message if logged in user owns message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = self.testuser.id
        )
        db.session.add(m)
        db.session.commit()

        resp = c.post("/messages/1/delete")

        self.assertEqual(resp.status_code, 302)

        self.assertEqual(len(self.testuser.messages), 0)

    def test_delete_message_fail(self):
        """Delete option not available if not owner of message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        exampleuser = User.query.get_or_404(2)

        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(exampleuser.messages), 1)

        resp = c.get("/messages/1")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(html, 'delete')
        
    def test_add_message_no_login(self):
        """Can a non-user add a message?"""
        with app.test_client() as client:
            resp = client.post('/messages/new', data={'text': "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            m = Message.query.all()
            # ensure message length is still 0
            self.assertEqual(len(m), 0)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.request.path, "/")    
            self.assertIn("Access unauthorized", html)
    
    def test_delete_message_no_login(self):
        """Can a non-user delete a message?"""
        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )

        db.session.add(m)

        m = Message.query.all()
        
        with app.test_client() as client:
            resp = client.post('/messages/1/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.request.path, "/")    
            self.assertIn("Access unauthorized", html)
            # messages length 1, message was not deleted
            self.assertEqual(len(m), 1)
           
    def test_add_message_to_user_no_login(self):
        """Can a non-user add a message to a user?"""

        u = User.query.get_or_404(2)

        with app.test_client() as client:
            resp = client.post('/messages/new', data={'text': "hello", "user_id": "2"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.request.path, "/")    
            self.assertIn("Access unauthorized", html)
            self.assertEqual(len(u.messages), 0)

    def test_delete_message_no_login(self):
        """Can a non-user delete a message by a user?"""
        u = User.query.get_or_404(2)

        m = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        db.session.add(m)
        db.session.commit()

        with app.test_client() as client:
            resp = client.post('/messages/1/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.request.path, "/")    
            self.assertIn("Access unauthorized", html)
            self.assertEqual(len(u.messages), 1)



    

