from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=100))
    category = fields.String(required=True)
    equipment_needed = fields.Boolean(load_default=False)

    @validates('name')
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('Name cannot be blank.')

    @validates('category')
    def validate_category(self, value, **kwargs):
        if value.strip().lower() not in EXERCISE_CATEGORIES:
            raise ValidationError(f"Category must be one of: {', '.join(EXERCISE_CATEGORIES)}.")


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(
        required=True, strict=True, validate=validate.Range(min=1, max=600))
    notes = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(max=1000))


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)
    reps = fields.Integer(
        allow_none=True, load_default=None, strict=True, validate=validate.Range(min=1))
    sets = fields.Integer(
        allow_none=True, load_default=None, strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(
        allow_none=True, load_default=None, strict=True, validate=validate.Range(min=1))

    # Read-only nested objects, trimmed with `only=` where each is used.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)

    @validates_schema
    def validate_prescription(self, data, **kwargs):
        """Require a timed duration, or both reps and sets."""
        has_duration = data.get('duration_seconds') is not None
        has_reps_and_sets = data.get('reps') is not None and data.get('sets') is not None
        if not (has_duration or has_reps_and_sets):
            raise ValidationError(
                'Provide duration_seconds, or both reps and sets.', field_name='_schema')


class WorkoutDetailSchema(WorkoutSchema):
    """A workout plus its exercises, including reps/sets/duration."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True,
        only=('id', 'reps', 'sets', 'duration_seconds', 'exercise'))


class ExerciseDetailSchema(ExerciseSchema):
    """An exercise plus the workouts it appears in."""
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True,
        only=('id', 'reps', 'sets', 'duration_seconds', 'workout'))
