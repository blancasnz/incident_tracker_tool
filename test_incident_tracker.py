"""Api tests for incident tracker"""

import pytest
from incident_tracker import app, db, Incident, Severity


@pytest.fixture()
def client():
    """Create test client"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client
            db.drop_all()


# Testing POST
def test_create_incident_success(client):
    """Test creating an incident"""

    data = {
        "title": "Test incident",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": "Medium",
    }

    response = client.post("/incidents", json=data)

    assert response.status_code == 201
    result = response.get_json()
    assert result["title"] == "Test incident"
    assert result["description"] == "Something broke"
    assert result["reported_by"] == "Trent"
    assert result["severity"] == "Medium"

    with app.app_context():
        assert Incident.query.count() == 1


def test_create_incident_missing_title(client):
    """Test creating an incident with missing required field title fails"""

    data = {
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    response = client.post("/incidents", json=data)

    assert response.status_code == 400
    result = response.get_json()
    assert result["missing"] == ["title"]

    with app.app_context():
        assert Incident.query.count() == 0


def test_create_incident_invalid_severity(client):
    """Test creating an incident with an invalid severity level fails"""

    data = {
        "title": "Test incident",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": "important",
    }

    response = client.post("/incidents", json=data)

    assert response.status_code == 400
    result = response.get_json()
    assert result["error"] == "Invalid severity"

    with app.app_context():
        assert Incident.query.count() == 0


# Testing GET
def test_get_incidents(client):
    """Test retrieving incidents with filter for status and severity"""

    incident_1 = {
        "title": "Test incident 1",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    incident_2 = {
        "title": "Test incident 2",
        "description": "Something broke again",
        "reported_by": "Trent",
        "severity": Severity.HIGH.value,
    }

    incident_3 = {
        "title": "Test incident 3",
        "description": "Something else broke",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    client.post("/incidents", json=incident_1)
    client.post("/incidents", json=incident_2)
    client.post("/incidents", json=incident_3)

    # no filters
    response_1 = client.get("/incidents")
    result_1 = response_1.get_json()
    assert result_1["total"] == 3

    # with severity filter
    response_2 = client.get("/incidents?severity=High")
    result_2 = response_2.get_json()
    assert result_2["total"] == 1

    # with severity and status filter
    response_2 = client.get("/incidents?severity=Medium&status=Open")
    result_2 = response_2.get_json()
    assert result_2["total"] == 2


# Testing PATCH
def test_update_incident_with_valid_status(client):
    """Test status update for an incident with a valid status"""

    data = {
        "title": "Test incident 1",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": Severity.LOW.value,
    }

    response = client.post("/incidents", json=data)
    result = response.get_json()
    assert result["status"] == "Open"
    incident_id = result["id"]

    update_data = {"status": "Resolved"}
    updated_response = client.patch(f"/incidents/{incident_id}", json=update_data)
    updated_result = updated_response.get_json()
    assert updated_result["status"] == "Resolved"
    assert updated_result["id"] == incident_id


def test_update_incident_with_invalid_status(client):
    """Test status update for an incident with an invalid status"""

    data = {
        "title": "Test incident 1",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    response = client.post("/incidents", json=data)
    result = response.get_json()
    assert result["status"] == "Open"
    incident_id = result["id"]

    update_data = {"status": "Working on it"}
    updated_response = client.patch(f"/incidents/{incident_id}", json=update_data)
    assert updated_response.status_code == 400
    updated_result = updated_response.get_json()
    assert updated_result["error"] == "Invalid status"


def test_update_nonexistent_incident(client):
    """ "Test updating an incident that doesn't exist"""
    fake_id = "1"
    update_data = {"status": "Resolved"}

    response = client.patch(f"/incidents/{fake_id}", json=update_data)
    assert response.status_code == 404
    result = response.get_json()
    assert result["error"] == "Incident not found"


# Testing DELETE
def test_delete_incident(client):
    """Test deleting an incident"""

    incident_1 = {
        "title": "Test incident 1",
        "description": "Something broke",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    incident_2 = {
        "title": "Test incident 2",
        "description": "Something broke again",
        "reported_by": "Trent",
        "severity": Severity.MEDIUM.value,
    }

    client.post("/incidents", json=incident_1)
    response = client.post("/incidents", json=incident_2)

    # Before deletion
    with app.app_context():
        assert Incident.query.count() == 2

    result = response.get_json()
    incident_id = result["id"]
    deletion = client.delete(f"/incidents/{incident_id}")
    deletion_result = deletion.get_json()

    # After deletion
    with app.app_context():
        assert Incident.query.count() == 1
    assert deletion_result["message"] == "Incident deleted successfully"
