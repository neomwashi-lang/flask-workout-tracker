from marshmallow import Schema, fields


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    category = fields.String(required=True)
    equipment_needed = fields.Boolean(load_default=False)


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    notes = fields.String(allow_none=True, load_default=None)


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)
    reps = fields.Integer(allow_none=True, load_default=None)
    sets = fields.Integer(allow_none=True, load_default=None)
    duration_seconds = fields.Integer(allow_none=True, load_default=None)

    # Read-only nested objects, trimmed with `only=` where each is used.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)


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
