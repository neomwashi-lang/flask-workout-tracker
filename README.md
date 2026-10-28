# Workout Tracker API

A Flask REST API for personal trainers to track workouts and the exercises in them.

## Description

Trainers can create and view workouts, build a reusable library of exercises, and add any
exercise to any workout with the reps, sets, or duration prescribed for that session.

- **Stack:** Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Marshmallow, SQLite
- **Models:** `Exercise`, `Workout`, and the `WorkoutExercise` join table
- **Validation at three levels:**
  - *Table constraints* (SQLite `CHECK`/`UNIQUE`): positive reps/sets/duration, workout duration
    between 1 and 600 minutes, allowed exercise categories, non-blank and unique exercise names,
    no duplicate exercise within a workout, and a prescription (duration, or reps and sets) is required
  - *Model validations* (`@validates`): the same rules enforced when objects are created in Python
  - *Schema validations* (Marshmallow): type, range, and required-field checks on request bodies,
    plus a cross-field check that a prescription is present

## Project structure

```
server/
  app.py        Flask app and routes
  models.py     SQLAlchemy models, relationships, constraints, validations
  schemas.py    Marshmallow schemas (serialization and validation)
  seed.py       Resets and populates the database with example data
  migrations/   Alembic migrations
tests/          pytest suite
```

## Installation

Requires Python 3.9+ and [pipenv](https://pipenv.pypa.io/).

```bash
pipenv install
pipenv shell
cd server
flask db upgrade head      # create the database from the included migration
python seed.py             # optional: load example data (safe to re-run)
```

To regenerate migrations from scratch instead, run `flask db init`,
`flask db migrate -m "message"`, then `flask db upgrade head` (set `FLASK_APP=app.py`).

## Running the server

```bash
cd server
flask run --port 5555
# or: python app.py
```

The API is then available at `http://localhost:5555`.

## Running the tests

```bash
pipenv install --dev
pipenv run pytest
```

## API endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show a workout with its exercises, including reps, sets, and duration |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout and its workout exercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show an exercise and the workouts it appears in |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout exercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps/sets or duration |

### Request bodies

Create a workout (`duration_minutes` is 1-600, `notes` is optional):

```json
{ "date": "2026-11-01", "duration_minutes": 45, "notes": "Upper body focus" }
```

Create an exercise (`category` is one of `strength`, `cardio`, `flexibility`, `balance`, `core`;
`equipment_needed` defaults to `false`):

```json
{ "name": "Bench Press", "category": "strength", "equipment_needed": true }
```

Add an exercise to a workout (provide `duration_seconds`, or both `reps` and `sets`):

```json
{ "reps": 8, "sets": 4 }
```

### Status codes

| Code | Meaning |
| ---- | ------- |
| 200 / 201 | Success / created |
| 204 | Deleted (no body) |
| 400 | Validation failed (response lists the errors) |
| 404 | Workout or exercise not found |
| 409 | Duplicate exercise name, or exercise already in that workout |
