# Incident Tracker API

A simple Incident Tracker tool for tracking internal system incidents.

## Technologies Used

- **Python** : Core programming language
- **Flask** : Web framework for REST API
- **SQLAlchemy** : ORM
- **SQLite** : Lightweight database
- **Pytest** : Testing framework

## Features

- Create, read, update, and delete incidents
- Filter incidents by status and severity
- SQLite database with persistent storage
- Validation and error handling
- Test coverage

## API Endpoints

- `POST /incidents` - Create a new incident
- `GET /incidents` - Get all incidents (optional filtering)
- `PATCH /incidents/<incident_id>` - Update an incident status
- `DELETE /incidents/<incident_id>` - Delete an incident

## Installation

1. Clone the repository

```bash
git clone https://github.com/blancasnz/incident_tracker_tool.git
```

2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
flask --app incident_tracker run --debug
```

The API will be available at `http://127.0.0.1:5000`

## Example Usage

#### With curl command or Postman

### 1. Create an incident

```bash
curl -X POST http://127.0.0.1:5000/incidents \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Page is broken",
        "description": "Users can not search for books",
        "reported_by": "Blanca@hiremeplease.com",
        "severity": "High"
    }'
```

Response will look something like:

```bash
{
  "description": "Users can not search for books",
  "id": 1,
  "reported_by": "Blanca@hiremeplease.com",
  "severity": "High",
  "status": "Open",
  "timestamp": "2025-09-06T20:52:35.521060",
  "title": "Page is broken"
}
```

### 2. Get all incidents (can see incident ID's)

```bash
curl http://127.0.0.1:5000/incidents
```

### 3. Update incident status (using ID from step 1 or 2)

```bash
curl -X PATCH http://127.0.0.1:5000/incidents/<incident_id> \
    -H "Content-Type: application/json" \
    -d '{"status": "Resolved"}'
```

### 4. Filter incidents

```bash
curl "http://127.0.0.1:5000/incidents?status=Resolved&severity=High"
```

## Data Model

### Incident Fields

- `id` : Integer (auto-generated)
- `title` : String (required)
- `description` : String (required)
- `reported_by` : String (required)
- `severity` : Enum ["Low", "Medium", "High"]
- `status` : Enum ["Open", "In Progress", "Resolved"] (default: "Open")
- `timestamp`: DateTime (auto-generated, UTC)

## Running Tests

```bash
pytest test_incident_tracker.py -v
```
