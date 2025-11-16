# pytest is not required to be imported in test modules
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Remove if already present
    if email in client.get("/activities").json()[activity]["participants"]:
        client.post(f"/activities/{activity}/unregister?email={email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Clean up
    client.post(f"/activities/{activity}/unregister?email={email}")


def test_signup_for_activity_already_signed_up():
    activity = "Chess Club"
    email = "michael@mergington.edu"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_for_activity_full():
    activity = "Chess Club"
    # Fill up the activity
    max_participants = client.get("/activities").json()[activity]["max_participants"]
    emails = [f"student{i}@mergington.edu" for i in range(max_participants)]
    # Remove all first
    for email in client.get("/activities").json()[activity]["participants"]:
        client.post(f"/activities/{activity}/unregister?email={email}")
    for email in emails:
        client.post(f"/activities/{activity}/signup?email={email}")
    # Try to add one more
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
    # Clean up
    for email in emails:
        client.post(f"/activities/{activity}/unregister?email={email}")
