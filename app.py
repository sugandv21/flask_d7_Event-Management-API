from flask import Flask, request, jsonify, redirect, url_for
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
api = Api(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)  
    location = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "date": self.date, "location": self.location}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return jsonify({"message": "Event Management API is running! Use /events to manage events."})

class EventListResource(Resource):
    def get(self):
        events = Event.query.all()
        return [event.to_dict() for event in events], 200

    def post(self):
        data = request.get_json()
        if not data.get("name") or not data.get("date") or not data.get("location"):
            return {"error": "All fields (name, date, location) are required"}, 400
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            return {"error": "Date must be in YYYY-MM-DD format"}, 400

        new_event = Event(name=data["name"], date=data["date"], location=data["location"])
        db.session.add(new_event)
        db.session.commit()
        return new_event.to_dict(), 201

class EventResource(Resource):
    def get(self, id):
        event = Event.query.get(id)
        if not event:
            return {"error": "Event not found"}, 404
        return event.to_dict(), 200

    def put(self, id):
        event = Event.query.get(id)
        if not event:
            return {"error": "Event not found"}, 404
        data = request.get_json()
        if "date" in data:
            try:
                datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                return {"error": "Date must be in YYYY-MM-DD format"}, 400
        event.name = data.get("name", event.name)
        event.date = data.get("date", event.date)
        event.location = data.get("location", event.location)
        db.session.commit()
        return event.to_dict(), 200

    def delete(self, id):
        event = Event.query.get(id)
        if not event:
            return {"error": "Event not found"}, 404
        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted"}, 200

api.add_resource(EventListResource, "/events", endpoint="events")
api.add_resource(EventResource, "/events/<int:id>", endpoint="event")

if __name__ == "__main__":
    app.run(debug=False)

