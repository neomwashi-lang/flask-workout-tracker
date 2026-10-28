#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():

    # Clear existing data (children first) so re-running never duplicates rows.
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Seeding exercises...')
    squat = Exercise(name='Barbell Squat', category='strength', equipment_needed=True)
    pushup = Exercise(name='Push-Up', category='strength', equipment_needed=False)
    deadlift = Exercise(name='Deadlift', category='strength', equipment_needed=True)
    plank = Exercise(name='Plank', category='core', equipment_needed=False)
    run = Exercise(name='Treadmill Run', category='cardio', equipment_needed=True)
    yoga = Exercise(name='Downward Dog', category='flexibility', equipment_needed=False)
    db.session.add_all([squat, pushup, deadlift, plank, run, yoga])

    print('Seeding workouts...')
    leg_day = Workout(date=date(2026, 10, 26), duration_minutes=60,
                      notes='Focus on depth and form. Client reported tight hips.')
    full_body = Workout(date=date(2026, 10, 27), duration_minutes=45,
                        notes='Light full-body session.')
    cardio_core = Workout(date=date(2026, 10, 28), duration_minutes=30)
    db.session.add_all([leg_day, full_body, cardio_core])

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, reps=8, sets=4),
        WorkoutExercise(workout=leg_day, exercise=deadlift, reps=5, sets=3),
        WorkoutExercise(workout=leg_day, exercise=yoga, duration_seconds=120),
        WorkoutExercise(workout=full_body, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=full_body, exercise=squat, reps=12, sets=3),
        WorkoutExercise(workout=full_body, exercise=plank, duration_seconds=60),
        WorkoutExercise(workout=cardio_core, exercise=run, duration_seconds=1200),
        WorkoutExercise(workout=cardio_core, exercise=plank, duration_seconds=90),
    ])

    db.session.commit()
    print(f'Done: {Exercise.query.count()} exercises, {Workout.query.count()} workouts, '
          f'{WorkoutExercise.query.count()} workout exercises.')
