#!/usr/bin/python3
from flask import Flask, request, jsonify, json
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname))
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SECRET_KEY'] = 'SuperSecretKey'

api = Api()

db = SQLAlchemy(app)
ma = Marshmallow(app)


def create_app():
    db.init_app(app)
    return app


with engine.connect() as connection:
    result = connection.execute("SELECT * FROM sys.user")
    for row in result:
        print("name: ", row['name'], "email: ", row['email'], "id:", row['id'])


def api_response():
    if request.method == 'POST':
        return jsonify(**request.json)


def user_serializer(user):
    return {'id': user.id,
            'name': user.name,
            'email': user.email,
            }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email
        super(User, self).__init__()

    def __repr__(self):
        return '<User % s > ' % self.email


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/api", methods=['GET'])
def api():
    return jsonify([*map(user_serializer, User.query.all())])


@app.route("/api/create", methods=['POST'])
def create():
    request_data = json.loads(request.data)
    print(request_data)
    addUser = User(name=request_data['name'], email=request_data['email'])
    db.session.add(addUser)
    db.session.commit()
    return "User Created"


if __name__ == "__main__":
    app.run(debug=True)

db.create_all()
