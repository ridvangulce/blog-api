#!/usr/bin/python3
import hashlib
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask import Flask, request, jsonify, json
from flask_restful import Api
from flask_security import UserMixin
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine
import bcrypt

engine = create_engine(
    "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname))
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SECRET_KEY'] = 'SuperSecretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api()
db = SQLAlchemy(app)
db.init_app(app)
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
            'password': user.password
            }


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, )
    email = db.Column(db.String(120), unique=True, )
    password = db.Column(db.String(120), )

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        super(User, self).__init__()

    def __repr__(self):
        return '<User % s > ' % self.email


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "password")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/api", methods=['GET'])
def api():
    return jsonify([*map(user_serializer, User.query.all())])


@app.route("/register", methods=['POST'])
def register():
    name = request.json.get('name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not name:
        return "Missing Name"
    if not email:
        return "Missing Email"
    if not password:
        return "Missing Password"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    addUser = User(name=name, email=email, password=hashed)
    db.session.add(addUser)
    db.session.commit()

    db.session.add(addUser)
    db.session.commit()
    return "User Created"


@app.route("/login", methods=['POST'])
def login():
    name = request.json.get('name', None)
    password = request.json.get('password', None)
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if not name:
        return "Missing Username", 400
    if not password:
        return "Missing Password", 400

    user = User.query.filter_by(name=name).first()
    if not user:
        return "User Not Found", 404

    if bcrypt.checkpw(password.encode('utf-8'), hashed):
        return "Welcome Back"

    else:
        return "Wrong Password"


if __name__ == "__main__":
    app.run(debug=True)

db.create_all()
