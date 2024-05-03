from flask_sqlalchemy import SQLAlchemy

# for timestamps
from datetime import datetime

db = SQLAlchemy()
# association tables
user_food_association = db.Table(
    "user_food_association",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("food_id", db.Integer, db.ForeignKey("food.id"), primary_key=True),
)

# your classes here


class User(db.Model):
    """
    User model
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    goal_weight = db.Column(db.Float, nullable=False)
    daily_calorie_target = db.Column(db.Integer, nullable=False)

    # cascades with user, if user deleted, delete the foods under user
    # foods = db.relationship("Food", cascade="delete")
    foods = db.relationship("Food", secondary=user_food_association, backref="users")

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.weight = kwargs.get("weight", 0.0)
        self.height = kwargs.get("height", 0.0)
        self.goal_weight = kwargs.get("goal_weight", 0.0)
        self.daily_calorie_target = kwargs.get("daily_calorie_target", 0)

    def user_serialize(self):
        """
        Serialize a user object
        """
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "height": self.height,
            "goal weight": self.goal_weight,
            "daily calorie target": self.daily_calorie_target,
            # for each food, serialize and store in list
            "foods": [f.serialize() for f in self.foods],
        }

    def get_food_entries_on_date(self, date):
        """
        Get all food entries logged on a certain date
        """
        return (
            Food.query.filter(Food.users.contains(self))
            .filter(Food.timestamp >= datetime.combine(date, datetime.min.time()))
            .filter(Food.timestamp < datetime.combine(date, datetime.max.time()))
            .all()
        )

    def total_calories_eaten_on_date(self, date):
        """
        Calculate the total calories eaten on a certain date
        """
        food_entries = self.get_food_entries_on_date(date)
        total_calories = sum(food.calories for food in food_entries)
        return total_calories

    def remaining_calories_for_day(self, date):
        """
        Calculate the remaining calories left for the day
        """
        total_calories_eaten = self.total_calories_eaten_on_date(date)
        remaining_calories = self.daily_calorie_target - total_calories_eaten
        return remaining_calories if remaining_calories >= 0 else 0


class Food(db.Model):
    """
    Food Model
    """

    __tablename__ = "food"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)

    calories = db.Column(db.Integer, nullable=False)

    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    users = db.relationship("User", secondary=user_food_association, backref="foods")

    # should 1-many connect to user
    # reference id of user table
    # FOREIGN KEY

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a food objects/entrys
        """
        self.name = kwargs.get("name", "")
        self.calories = kwargs.get("calories", 0)
        self.carbs = kwargs.get("carbs", 0.0)
        self.fat = kwargs.get("fat", 0.0)
        self.protein = kwargs.get("protein", 0.0)

        # self.user_id = kwargs.get("user_id")

    def food_serialize(self):
        """
        Serialize a food object
        """
        return {
            "id": self.id,
            "name": self.name,
            "calories": self.calories,
            "carbs": self.carbs,
            "fat": self.fat,
            "protein": self.protein,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
