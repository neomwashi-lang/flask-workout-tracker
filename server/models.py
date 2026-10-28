from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Allowed exercise categories (enforced by both a model validation and a table constraint).
EXERCISE_CATEGORIES = ('strength', 'cardio', 'flexibility', 'balance', 'core')


class Exercise(db.Model):
    __tablename__ = 'exercises'

    __table_args__ = (
        db.CheckConstraint('length(trim(name)) > 0', name='ck_exercises_name_not_blank'),
        db.CheckConstraint(
            "category IN ('strength', 'cardio', 'flexibility', 'balance', 'core')",
            name='ck_exercises_category_allowed'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Deleting an exercise also deletes its WorkoutExercise rows.
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')
    workouts = association_proxy('workout_exercises', 'workout')

    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Exercise name must be a non-empty string.')
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        if not isinstance(value, str) or value.strip().lower() not in EXERCISE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXERCISE_CATEGORIES)}.")
        return value.strip().lower()

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    __table_args__ = (
        db.CheckConstraint(
            'duration_minutes > 0 AND duration_minutes <= 600',
            name='ck_workouts_duration_range'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Deleting a workout also deletes its WorkoutExercise rows.
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')
    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('Workout date must be a date.')
        return value

    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 < value <= 600:
            raise ValueError('Duration must be a whole number of minutes between 1 and 600.')
        return value

    @validates('notes')
    def validate_notes(self, key, value):
        if value is not None and len(value) > 1000:
            raise ValueError('Notes must be 1000 characters or fewer.')
        return value

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    """Join table linking a workout to an exercise, with the prescription
    (reps/sets and/or duration) for that exercise in that workout."""
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        # The same exercise can only be added to a given workout once.
        db.UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise_pair'),
        db.CheckConstraint('reps IS NULL OR reps > 0', name='ck_workout_exercises_reps_positive'),
        db.CheckConstraint('sets IS NULL OR sets > 0', name='ck_workout_exercises_sets_positive'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0',
            name='ck_workout_exercises_duration_positive'),
        # Must prescribe either a timed duration, or both reps and sets.
        db.CheckConstraint(
            'duration_seconds IS NOT NULL OR (reps IS NOT NULL AND sets IS NOT NULL)',
            name='ck_workout_exercises_has_prescription'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive_int(self, key, value):
        if value is None:
            return value
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f'{key} must be a positive whole number.')
        return value

    def __repr__(self):
        return f'<WorkoutExercise {self.id}: workout={self.workout_id} exercise={self.exercise_id}>'
