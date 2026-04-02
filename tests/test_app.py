from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: keep a snapshot of initial activities state
    original = {activity: {
        "description": details["description"],
        "schedule": details["schedule"],
        "max_participants": details["max_participants"],
        "participants": list(details["participants"]),
    } for activity, details in activities.items()}

    yield

    activities.clear()
    activities.update({activity: {
        "description": details["description"],
        "schedule": details["schedule"],
        "max_participants": details["max_participants"],
        "participants": list(details["participants"]),
    } for activity, details in original.items()})

@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_index(client):
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (200, 307, 308)
    if response.status_code in (307, 308):
        assert response.headers["location"] == "/static/index.html"



def test_get_activities_returns_all_activities(client):
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "Chess Club" in response_data
    assert "Programming Class" in response_data


def test_signup_for_activity_success(client):
    # Arrange
    email = "testuser@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found_returns_404(client):
    # Act
    response = client.post("/activities/NoActivity/signup", params={"email": "new@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_success(client):
    # Arrange
    email = "john@mergington.edu"

    # Act
    response = client.delete("/activities/Gym Class/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Gym Class"}
    assert email not in activities["Gym Class"]["participants"]


def test_unregister_not_registered_returns_404(client):
    # Act
    response = client.delete("/activities/Gym Class/participants", params={"email": "notfound@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_activity_not_found_returns_404(client):
    # Act
    response = client.delete("/activities/Invalid Activity/participants", params={"email": "test@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"