"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Tests for the /activities endpoints"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0

    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_activity_has_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) > 0
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for the signup endpoint"""

    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Science%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_updates_participants(self, client):
        """Test that signup adds participant to activity"""
        email = "teststudent1@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Art%20Studio/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Art Studio"]["participants"]

    def test_signup_duplicate_email_fails(self, client):
        """Test that signing up with duplicate email fails"""
        email = "newstudent2@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Debate%20Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Debate%20Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        activity = "Tennis Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Sign up first student
        response1 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        
        # Verify both are in participants
        response = client.get("/activities")
        data = response.json()
        assert email1 in data[activity]["participants"]
        assert email2 in data[activity]["participants"]


class TestUnregister:
    """Tests for the unregister endpoint"""

    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        email = "student3@mergington.edu"
        
        # First, sign up
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "student4@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        
        # Verify they're signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister",
            params={"email": email}
        )
        
        # Verify they're no longer signed up
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_unregistered_student_fails(self, client):
        """Test that unregistering a non-registered student fails"""
        response = client.delete(
            "/activities/Gym%20Class/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_index(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
