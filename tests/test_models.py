from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db


def run_sql(sql):
    """Execute raw SQL, bypassing model validations to exercise table constraints."""
    db.session.execute(text(sql))
    db.session.commit()


# ------------------------------------------------------------ relationships

def test_relationships(app):
    workout = Workout(date=date(2026, 1, 1), duration_minutes=30)
    exercise = Exercise(name='Squat', category='strength')
    db.session.add(WorkoutExercise(workout=workout, exercise=exercise, reps=5, sets=3))
    db.session.commit()

    assert workout.exercises == [exercise]
    assert exercise.workouts == [workout]
    assert workout.workout_exercises[0].exercise is exercise


# ------------------------------------------------------- model validations

@pytest.mark.parametrize('name', ['', '   '])
def test_exercise_rejects_blank_name(app, name):
    with pytest.raises(ValueError):
        Exercise(name=name, category='core')


def test_exercise_rejects_unknown_category(app):
    with pytest.raises(ValueError):
        Exercise(name='Mystery', category='magic')


@pytest.mark.parametrize('minutes', [0, -5, 601, '30', True])
def test_workout_rejects_bad_duration(app, minutes):
    with pytest.raises(ValueError):
        Workout(date=date.today(), duration_minutes=minutes)


def test_workout_exercise_rejects_non_positive_numbers(app):
    with pytest.raises(ValueError):
        WorkoutExercise(reps=0)
    with pytest.raises(ValueError):
        WorkoutExercise(duration_seconds=-10)


# ------------------------------------------------------- table constraints

def test_db_rejects_blank_exercise_name(app):
    with pytest.raises(IntegrityError):
        run_sql("INSERT INTO exercises (name, category, equipment_needed) VALUES (' ', 'core', 0)")


def test_db_rejects_unknown_category(app):
    with pytest.raises(IntegrityError):
        run_sql("INSERT INTO exercises (name, category, equipment_needed) VALUES ('a', 'zzz', 0)")


def test_db_rejects_duplicate_exercise_name(app):
    run_sql("INSERT INTO exercises (name, category, equipment_needed) VALUES ('a', 'core', 0)")
    with pytest.raises(IntegrityError):
        run_sql("INSERT INTO exercises (name, category, equipment_needed) VALUES ('a', 'core', 0)")


def test_db_rejects_out_of_range_duration(app):
    with pytest.raises(IntegrityError):
        run_sql("INSERT INTO workouts (date, duration_minutes) VALUES ('2026-01-01', 999)")


def test_db_rejects_missing_prescription_and_duplicate_pairs(app):
    run_sql("INSERT INTO exercises (name, category, equipment_needed) VALUES ('a', 'core', 0)")
    run_sql("INSERT INTO workouts (date, duration_minutes) VALUES ('2026-01-01', 30)")
    with pytest.raises(IntegrityError):
        run_sql('INSERT INTO workout_exercises (workout_id, exercise_id) VALUES (1, 1)')
    db.session.rollback()
    run_sql('INSERT INTO workout_exercises (workout_id, exercise_id, reps, sets) VALUES (1, 1, 5, 5)')
    with pytest.raises(IntegrityError):
        run_sql('INSERT INTO workout_exercises (workout_id, exercise_id, reps, sets) VALUES (1, 1, 8, 2)')
