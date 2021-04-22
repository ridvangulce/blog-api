#!/usr/bin/python3
from flask import Flask, request, jsonify, redirect, url_for
from flask_restful import Api
from flask_security import UserMixin
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname))
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.secret_key = b'7ash2i%5pk2159=p4!12op44221*rwWQcs'
app.config["JWT_SECRET_KEY"] = "1823h2#1i123l!'d#s8h89iIOD2#£j"
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SECRET_KEY'] = '2o1£21ıoj2£#31ıj1#23l)Da9djs!e'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api()
db = SQLAlchemy(app)
db.init_app(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
Session = sessionmaker(bind=engine)
bcrypt = Bcrypt(app)


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
    token = db.Column(db.String(120), )

    def __init__(self, name, email, password, token):
        self.name = name
        self.email = email
        self.password = password
        self.token = token
        super(User, self).__init__()

    def __repr__(self):
        return '<User % s > ' % self.email


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "password", "token")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/api", methods=['GET'])
def api():
    return jsonify([*map(user_serializer, User.query.all())])


@app.route("/register", methods=['POST', 'GET'])
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
    access_token = create_access_token(identity=name)
    hashed = bcrypt.generate_password_hash(password.encode('utf-8'))
    addUser = User(name=name, email=email, password=hashed, token=access_token)
    db.session.add(addUser)
    db.session.commit()
    return "User Created"


@app.route("/login", methods=['POST', 'GET'])
def login():
    name = request.json.get('name', None)
    password = request.json.get('password', None)
    if not name:
        return "Missing Username", 400
    if not password:
        return "Missing Password", 400
    user = User.query.filter_by(name=name).first()
    print(user)

    if not user:
        return "User Not Found", 404

    if user and bcrypt.check_password_hash(user.password, password):
        return "Welcome Back"

    else:
        return "Wrong Password"


@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    return "Welcome"


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
    app.run(debug=True)

db.create_all()
