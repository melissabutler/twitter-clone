import os
from unittest import TestCase

from models import db, User, Follows, Message
 
 
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all() 

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
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

        examplemessage = Message(
            id = 1,
            text= "Example Text",
            user_id = 2
        )
        db.session.add(examplemessage)
      

        db.session.commit()
    
    def test_view_home_signup_prompt(self):
        """Does a non-logged in user see the login prompt?"?"""
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('New to Warbler?', html)
        
    def test_view_home_messages_fail(self):
        """Can a non-logged in user see messages?"""
        exampleuser = User.query.get_or_404(2)
        examplemessage = Message.query.get_or_404(1)

        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # example message does not populate into html
            self.assertNotIn("Example Text", html)

    def test_view_home_login(self):
        """Does a logged in user see messages on the home page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        exampleuser = User.query.get_or_404(2)
        # have testuser follow example user so their message should appear
        self.testuser.following.append(exampleuser)

        resp = c.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("New to Warbler?", html)
        self.assertIn("Example Text", html)

    def test_view_followers(self):
        """Can user see their followers when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        exampleuser = User.query.get_or_404(2)

        self.testuser.followers.append(exampleuser)

        resp = c.get(f'/users/{self.testuser.id}/followers')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("exampleuser", html)

    def test_view_following(self):
        """Can user see who they are following when logged in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        exampleuser = User.query.get_or_404(2)

        self.testuser.following.append(exampleuser)

        resp = c.get(f'/users/{self.testuser.id}/following')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("exampleuser", html)
    
    def test_view_followers_fail(self):
        """ Can other user see user's followers?"""
        with app.test_client() as client:

            resp = client.get(f'/users/{self.testuser.id}/followers')
            html = resp.get_data(as_text=True)
            
            exampleuser = User.query.get_or_404(2)

            self.testuser.following.append(exampleuser)
        
            
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('exampleuser', html)
    
    def test_view_following_fail(self):
        """Can other user see user's following?"""
        with app.test_client() as client:

            resp = client.get(f'/users/{self.testuser.id}/following')
            html = resp.get_data(as_text=True)
            
            exampleuser = User.query.get_or_404(2)

            self.testuser.followers.append(exampleuser)
        
            
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('exampleuser', html)

    def test_user_view_no_login(self):
        """Can a non-logged in user see follow buttons on a profile?"""
        with app.test_client() as client:

            resp = client.get(f'/users/{self.testuser.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<button class="btn btn-outline-primary">Follow</button>', html)
