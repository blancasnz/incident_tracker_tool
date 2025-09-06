"""
Incident Tracker API with SQLite + SQLAlchemy
Take Home Assignment - Penguin Randomhouse
"""

from datetime import datetime, timezone
from enum import Enum

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Severity(Enum):
    """Enums for incident severity levels"""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(Enum):
    """Enums for incident status values"""

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class Incident(db.Model):
    """Incident database model"""

    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reported_by = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Open")
    timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )

    def __init__(self, title, description, reported_by, severity):
        self.title = title
        self.description = description
        self.reported_by = reported_by
        self.severity = severity
        self.status = Status.OPEN.value
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert incident to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reported_by": self.reported_by,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
        }


def validate_fields(data):
    """Check to see that all fields required to create an incident exist"""
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    missing = [
        k
        for k in ("title", "description", "reported_by")
        if not data.get(k) or not data.get(k).strip()
    ]
    if missing:
        return jsonify({"error": "Missing required field(s)", "missing": missing}), 400

    valid_severity = [severity.value for severity in Severity]
    if "severity" in data and data["severity"] not in valid_severity:
        return (
            jsonify(
                {
                    "error": "Invalid severity",
                    "message": f"Severity must be {valid_severity}",
                }
            ),
            400,
        )
    return None


@app.route("/incidents", methods=["POST"])
def create_incident():
    """Create a new incident"""
    data = request.get_json()
    err = validate_fields(data)
    if err:
        return err

    incident = Incident(
        title=data["title"],
        description=data["description"],
        reported_by=data["reported_by"],
        severity=data.get("severity", Severity.MEDIUM.value),
    )

    db.session.add(incident)
    db.session.commit()

    return jsonify(incident.to_dict()), 201


@app.route("/incidents", methods=["GET"])
def get_incidents():
    """Return a list of all incidents, filtered if filters passed"""
    incidents = Incident.query

    status_filter = request.args.get("status")
    severity_filter = request.args.get("severity")

    if status_filter:
        incidents = incidents.filter(Incident.status == status_filter)
    if severity_filter:
        incidents = incidents.filter(Incident.severity == severity_filter)

    incidents = incidents.order_by(Incident.timestamp.desc()).all()
    incident_list = [incident.to_dict() for incident in incidents]

    return jsonify({"incidents": incident_list, "total": len(incident_list)}), 200


@app.route("/incidents/<incident_id>", methods=["PATCH"])
def update_incident(incident_id):
    """Update an incident status"""
    incident = db.session.get(Incident, incident_id)

    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    valid_statuses = [status.value for status in Status]
    if "status" in data and data["status"] not in valid_statuses:
        return (
            jsonify(
                {
                    "error": "Invalid status",
                    "message": f"Status must be {valid_statuses}",
                }
            ),
            400,
        )

    if "status" in data:
        incident.status = data["status"]

    db.session.commit()
    return (jsonify(incident.to_dict())), 200


@app.route("/incidents/<incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    """Delete an incident"""
    incident = db.session.get(Incident, incident_id)

    if not incident:
        return (jsonify({"error": "Incident not found"})), 404

    incident_dict = incident.to_dict()
    db.session.delete(incident)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Incident deleted successfully",
                "deleted_incident": incident_dict,
            }
        ),
        200,
    )


# Initialize database
with app.app_context():
    db.create_all()
