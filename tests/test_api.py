from models import WorkoutExercise

WORKOUT = {'date': '2026-11-01', 'duration_minutes': 40, 'notes': 'Upper body'}
EXERCISE = {'name': 'Bench Press', 'category': 'strength', 'equipment_needed': True}


def make_workout(client, **overrides):
    return client.post('/workouts', json={**WORKOUT, **overrides}).get_json()


def make_exercise(client, **overrides):
    return client.post('/exercises', json={**EXERCISE, **overrides}).get_json()


def link(client, workout_id, exercise_id, **body):
    return client.post(f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises', json=body)


# ---------------------------------------------------------------- workouts

def test_create_and_list_workouts(client):
    response = client.post('/workouts', json=WORKOUT)
    assert response.status_code == 201
    assert response.get_json()['id'] == 1
    assert len(client.get('/workouts').get_json()) == 1


def test_create_workout_validation_errors(client):
    assert client.post('/workouts', json={'duration_minutes': 30}).status_code == 400
    assert client.post('/workouts', json={**WORKOUT, 'duration_minutes': 0}).status_code == 400
    assert client.post('/workouts', json={**WORKOUT, 'date': 'nope'}).status_code == 400
    assert client.post('/workouts', data='not json').status_code == 400


def test_get_workout_includes_exercise_details(client):
    workout, exercise = make_workout(client), make_exercise(client)
    link(client, workout['id'], exercise['id'], reps=8, sets=4)

    data = client.get(f"/workouts/{workout['id']}").get_json()
    entry = data['workout_exercises'][0]
    assert entry['reps'] == 8 and entry['sets'] == 4
    assert entry['exercise']['name'] == 'Bench Press'


def test_get_missing_workout_returns_404(client):
    assert client.get('/workouts/999').status_code == 404


def test_delete_workout_removes_workout_exercises(client, app):
    workout, exercise = make_workout(client), make_exercise(client)
    link(client, workout['id'], exercise['id'], reps=8, sets=4)

    assert client.delete(f"/workouts/{workout['id']}").status_code == 204
    assert client.get(f"/workouts/{workout['id']}").status_code == 404
    assert WorkoutExercise.query.count() == 0
    assert client.get(f"/exercises/{exercise['id']}").status_code == 200
    assert client.delete('/workouts/999').status_code == 404


# --------------------------------------------------------------- exercises

def test_create_and_list_exercises(client):
    assert client.post('/exercises', json=EXERCISE).status_code == 201
    assert len(client.get('/exercises').get_json()) == 1


def test_create_exercise_validation_errors(client):
    assert client.post('/exercises', json={'name': 'x'}).status_code == 400
    assert client.post('/exercises', json={'name': '  ', 'category': 'core'}).status_code == 400
    assert client.post('/exercises', json={'name': 'x', 'category': 'magic'}).status_code == 400


def test_duplicate_exercise_name_returns_409(client):
    make_exercise(client)
    assert client.post('/exercises', json=EXERCISE).status_code == 409


def test_get_exercise_includes_workouts(client):
    workout, exercise = make_workout(client), make_exercise(client)
    link(client, workout['id'], exercise['id'], duration_seconds=60)

    data = client.get(f"/exercises/{exercise['id']}").get_json()
    entry = data['workout_exercises'][0]
    assert entry['duration_seconds'] == 60
    assert entry['workout']['id'] == workout['id']
    assert client.get('/exercises/999').status_code == 404


def test_delete_exercise_removes_workout_exercises(client, app):
    workout, exercise = make_workout(client), make_exercise(client)
    link(client, workout['id'], exercise['id'], reps=8, sets=4)

    assert client.delete(f"/exercises/{exercise['id']}").status_code == 204
    assert WorkoutExercise.query.count() == 0
    assert client.get(f"/workouts/{workout['id']}").get_json()['workout_exercises'] == []
    assert client.delete('/exercises/999').status_code == 404


# ------------------------------------------------------ add to workout

def test_add_exercise_to_workout(client):
    workout, exercise = make_workout(client), make_exercise(client)
    response = link(client, workout['id'], exercise['id'], reps=10, sets=3)
    assert response.status_code == 201
    body = response.get_json()
    assert body['workout_id'] == workout['id'] and body['exercise_id'] == exercise['id']


def test_same_exercise_can_be_used_in_many_workouts(client):
    exercise = make_exercise(client)
    for day in ('2026-11-01', '2026-11-02'):
        workout = make_workout(client, date=day)
        assert link(client, workout['id'], exercise['id'], reps=5, sets=5).status_code == 201
    assert len(client.get(f"/exercises/{exercise['id']}").get_json()['workout_exercises']) == 2


def test_add_exercise_rejects_bad_input(client):
    workout, exercise = make_workout(client), make_exercise(client)
    assert link(client, workout['id'], exercise['id']).status_code == 400
    assert link(client, workout['id'], exercise['id'], reps=5).status_code == 400
    assert link(client, workout['id'], exercise['id'], reps=-1, sets=3).status_code == 400
    assert link(client, 999, exercise['id'], reps=5, sets=3).status_code == 404
    assert link(client, workout['id'], 999, reps=5, sets=3).status_code == 404


def test_add_same_exercise_twice_returns_409(client):
    workout, exercise = make_workout(client), make_exercise(client)
    link(client, workout['id'], exercise['id'], reps=5, sets=3)
    assert link(client, workout['id'], exercise['id'], reps=5, sets=3).status_code == 409
