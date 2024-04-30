import json

from datetime import datetime
# Added model/classes here
from db import db, User, Food
from flask import Flask, request


app = Flask(__name__)
db_filename = "nutritrack.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

#responses 
# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# your routes here
@app.route("/")

# Get All Food
@app.route("/api/foods/", methods=["GET"])
def get_all_foods():
    """
    Endpoint for getting all food logged
    """
    
    return success_response({"foods":[f.food_serialize() for f in Food.query.all()]})

# Create New Food 
# Not working? ? change to user_id for rest?  "/api/user/<int:user_id>/foods/"
@app.route("/api/foods/", methods=["POST"])
def create_food():
    """
    Endpoint for Creating Food
    """
    # add user_id to the params? search by user id
    #however there are only 1 user 

    # user = User.query.filter_by(id=user_id). first()
    # if user is None:
    #     return failure_response("user not found")

    body = json.loads(request.data)

    new_food = Food(
        name = body.get("name"),
        calories = body.get("calories"),
        carbs = body.get("carbs"),
        protein = body.get("protein"),
        fat = body.get("fat"),
        # add timestamp?
        timestamp = datetime.utcnow()

    )

    db.session.add(new_food)
    db.session.commit()

    return success_response(new_food.food_serialize(), 201)
    
# Get food by id 
@app.route("/api/foods/<int:food_id>/", methods=["GET"])
def get_course(food_id):
    """
    Endpoint - get food by id
    """

    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return failure_response("Dish not found")
    return success_response(food.food_serialize())


# Delete  Food
@app.route("/api/foods/<int:food_id>/", methods=["DELETE"])
def delete_course(food_id):
    """
    Endpoint - delete food by id
    """
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return failure_response("Dish not found")

    db.session.delete(food)
    db.session.commit()
    return success_response(food.food_serialize())

# Create User
@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)

    new_user = User(
        name = body.get("name"),
        weight = body.get("weight"),
        height = body.get("height"),
        goal_weight = body.get("goal_weight")
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.user_serialize(), 201)
# Get a user by ID
@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user_by_id(user_id):
    """
    Endpoint - get user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.user_serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
