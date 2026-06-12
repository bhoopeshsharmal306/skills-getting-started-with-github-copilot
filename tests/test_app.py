import copy

from httpx import Client
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    with Client(app=app, base_url="http://testserver") as client:
        response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_activity_adds_participant():
    email = "newstudent@mergington.edu"
    with Client(app=app, base_url="http://testserver") as client:
        response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    with Client(app=app, base_url="http://testserver") as client:
        data = client.get("/activities").json()

    assert email in data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "emma@mergington.edu"
    with Client(app=app, base_url="http://testserver") as client:
        response = client.post("/activities/Programming%20Class/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_remove_participant():
    email = "daniel@mergington.edu"
    with Client(app=app, base_url="http://testserver") as client:
        response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    with Client(app=app, base_url="http://testserver") as client:
        data = client.get("/activities").json()

    assert email not in data["Chess Club"]["participants"]
