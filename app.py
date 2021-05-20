#!/usr/bin/python3
from datetime import timedelta

from flask import Flask, request, jsonify, session
from flask_restful import Api
from flask_security import UserMixin
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

engine = create_engine(
    "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname))
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
app = Flask(__name__)
app.secret_key = b'7ash2i%5pk2159=p4!12op44221321*3123213313rwWQcs'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SECRET_KEY'] = '2o1£21ıoj2£#31ıj1#23l)Da9djs!e'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config["JWT_SECRET_KEY"] = "2o1£21ıoj2£#31ı12k3130o210*321"

jwt = JWTManager(app)
api = Api()
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
db.init_app(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
Session = sessionmaker()
Session.configure(bind=engine)


def create_app():
    db.init_app(app)
    return app


with engine.connect() as connection:
    result = connection.execute("SELECT * FROM sys.user")
    for row in result:
        print("name: ", row['name'], "email: ", row['email'], "id:", row['id'], "age:", row['age'])


def api_response():
    if request.method == 'POST':
        return jsonify(**request.json)


def user_serializer(user):
    return {'id': user.id,
            'name': user.name,
            'email': user.email,
            'password': user.password,
            'age': user.age
            }


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, )
    email = db.Column(db.String(120), unique=True, )
    password = db.Column(db.String(120), )
    age = db.Column(db.Integer)

    def __init__(self, name, email, password, age):
        self.name = name
        self.email = email
        self.password = password
        self.age = age
        super(User, self).__init__()

    def __repr__(self):
        return '<User % s > ' % self.email, self.age


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "password", "age")


users_schema = UserSchema(many=True)


@app.route("/api", methods=['GET'])
def api():

    return jsonify([*map(user_serializer, User.query.all())])


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name = request.json.get('name', None)
        email = request.json.get('email', None)
        age = request.json.get('age')
        password = request.json.get('password', None)
        if not name:
            return "Missing Name"
        if not email:
            return "Missing Email"
        if not password:
            return "Missing Password"
        if not age:
            return "Missing Age"
        hashed = bcrypt.generate_password_hash(password.encode('utf-8'))
        session["2o1£21ıoj2£#31ı12k3130o210*321"] = name
        addUser = User(name=name, email=email, password=hashed, age=age)
        create_access_token(identity=name)
        db.session.add(addUser)
        db.session.commit()
        return "user created"


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.json.get('name', None)
        password = request.json.get('password', None)
        bcrypt.generate_password_hash(password.encode('utf-8'))
        user = User.query.filter_by(name=name).first()
        session["2o1£21ıoj2£#31ı12k3130o210*321"] = name
        create_access_token(identity=name)
        if not name:
            return "Missing Username", 400
        if not password:
            return "Missing Password", 400
        if not user:
            return "User Not Found", 404

        if user and bcrypt.check_password_hash(user.password, password):
            return "Welcome"

        else:
            return "Wrong Password"


@app.route("/profile", methods=["GET", "POST"])
def welcome():
    session.pop('2o1£21ıoj2£#31ı12k3130o210*321', None)
    return "Logout Successfully"


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
    app.run(debug=True)

db.create_all()
