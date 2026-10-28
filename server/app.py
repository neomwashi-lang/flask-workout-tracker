import os

from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (
    ExerciseDetailSchema, ExerciseSchema, WorkoutDetailSchema,
    WorkoutExerciseSchema, WorkoutSchema,
)

app = Flask(__name__)
# DATABASE_URL lets the test suite point at an in-memory database.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

workout_schema = WorkoutSchema()
workout_detail_schema = WorkoutDetailSchema()
exercise_schema = ExerciseSchema()
exercise_detail_schema = ExerciseDetailSchema()
workout_exercise_schema = WorkoutExerciseSchema()


def error_response(message, status):
    return make_response({'error': message}, status)


def get_json_body():
    """Return the request's JSON object, or an empty dict if it is missing or not an object."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------- Workouts

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id).all()
    return make_response(WorkoutSchema(many=True).dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return error_response(f'Workout {id} not found.', 404)
    return make_response(workout_detail_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(get_json_body())
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValidationError as err:
        return make_response({'errors': err.messages}, 400)
    except ValueError as err:  # raised by model validations
        db.session.rollback()
        return error_response(str(err), 400)
    except IntegrityError:
        db.session.rollback()
        return error_response('Workout violates a database constraint.', 400)
    return make_response(workout_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return error_response(f'Workout {id} not found.', 404)
    # The relationship cascade also removes this workout's WorkoutExercises.
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# --------------------------------------------------------------- Exercises

@app.route('/exercises', methods=['GET'])
def get_exercises():
    return make_response({'message': 'not implemented'}, 501)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    return make_response({'message': 'not implemented'}, 501)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    return make_response({'message': 'not implemented'}, 501)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    return make_response({'message': 'not implemented'}, 501)


# -------------------------------------------------------- Workout exercises

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
           methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    return make_response({'message': 'not implemented'}, 501)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
