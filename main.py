from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
import json
from marshmallow import ValidationError

app = Flask(__name__)

with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Advocate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), unique=True)
    sex = db.Column(db.String(10))
    age = db.Column(db.Integer, unique=False)
    years_of_experience = db.Column(db.Integer, unique=False)
    salary = db.Column(db.Integer, unique=False)

    def __init__(self, full_name: str, sex: int, age: int, years_of_experience: int, salary: int):
        self.full_name = full_name
        self.sex = sex
        self.age = age
        self.years_of_experience = years_of_experience
        self.salary = salary

    def update(self, full_name: str, sex: int, age: int, years_of_experience: int, salary: int):
        self.__init__(full_name, sex, age, years_of_experience, salary)


def get_advocate_by_id(id):
    advocate = Advocate.query.get(id)
    if not advocate:
        return abort(404)
    return advocate


class AdvocateSchema(ma.Schema):
    full_name = fields.String()
    sex = fields.String()
    age = fields.Integer()
    years_of_experience = fields.Integer()
    salary = fields.Integer()


advocate_schema = AdvocateSchema()
advocates_schema = AdvocateSchema(many=True)


@app.route('/advocate', methods=['POST'])
def add_advocate():
    try:
        info_about_class = AdvocateSchema().load(request.json)
        advocate = Advocate(**info_about_class)
    except ValidationError:
        abort(400)
    db.session.add(advocate)
    db.session.commit()
    return advocate_schema.jsonify(advocate)


@app.route('/advocate/<id>', methods=['GET'])
def get_advocate(id):
    advocate = get_advocate_by_id(id)
    if not advocate:
        abort(404)
    return advocate_schema.jsonify(advocate)


@app.route('/advocate', methods=['GET'])
def get_advocates():
    all_advocates = Advocate.query.all()
    if not all_advocates:
        return abort(404)
    result = advocates_schema.dump(all_advocates)
    return advocates_schema.jsonify(result)


@app.route('/advocate/<id>', methods=['PUT'])
def update_advocate(id):
    advocate = get_advocate_by_id(id)
    if not advocate:
        abort(404)
    fields = advocate_schema.load(request.json)
    advocate.update(**fields)
    db.session.commit()
    return advocate_schema.jsonify(advocate)


@app.route('/advocate/<id>', methods=['DELETE'])
def delete_advocate(id):
    advocate = get_advocate_by_id(id)
    if not advocate:
        abort(404)
    db.session.delete(advocate)
    db.session.commit()
    return advocate_schema.jsonify(advocate)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
