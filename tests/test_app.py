import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 4,
            "participants": ["student@example.com"],
        },
        "Art Club": {
            "description": "Explore visual arts",
            "schedule": "Wednesdays at 3:30 PM",
            "max_participants": 6,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


def test_get_activities_returns_all_activities(reset_activities):
    # Arrange
    expected_activities = reset_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(reset_activities):
    # Arrange
    activity_name = "Art Club"
    email = "newstudent@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in reset_activities[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "expected_status", "expected_detail"),
    [
        ("Unknown Club", "student@example.com", 404, "Activity not found"),
        (
            "Chess Club",
            "student@example.com",
            400,
            "Student is already signed up for this activity",
        ),
    ],
)
def test_signup_rejects_invalid_requests(
    activity_name, email, expected_status, expected_detail
):
    # Arrange
    encoded_activity_name = activity_name.replace(" ", "%20")

    # Act
    response = client.post(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_remove_participant_removes_student_from_activity(reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Canceled {email}'s signup for {activity_name}"
    }
    assert email not in reset_activities[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "expected_detail"),
    [
        ("Unknown Club", "student@example.com", "Activity not found"),
        (
            "Art Club",
            "student@example.com",
            "Student is not signed up for this activity",
        ),
    ],
)
def test_remove_participant_rejects_invalid_requests(
    activity_name, email, expected_detail
):
    # Arrange
    encoded_activity_name = activity_name.replace(" ", "%20")

    # Act
    response = client.delete(
        f"/activities/{encoded_activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": expected_detail}