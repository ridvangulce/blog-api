#!/usr/bin/python3
from flask import Flask, request, redirect, url_for, render_template, jsonify, render_template, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy, Model
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


def create_user():
    name = request.form.get("name")
    email = request.form.get("email")
    user = User(name, email)
    db.session.add(user)
    db.commit


def update_user(user_id, data):
    user = User.query.filter(User.id == user_id).first()
    user.email = data.get('email')
    user.password = data.get('name')

    db.session.add(user)
    db.session.commit()


def delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()

    db.session.delete(user)
    db.session.commit()


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


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        return redirect(url_for("api"))

    else:
        return render_template("index.html")


@app.route("/api", methods=['GET'])
def api():
    with engine.connect() as connection:
        result = connection.execute("SELECT * FROM sys.user")
        records = result.fetchall()
        for row in records:
            print("name: ", row['name'], "email: ", row['email'], "id:", row['id'])

        return jsonify("name: ", row['name'], "email: ", row['email'], "id:", row['id'])


if __name__ == "__main__":
    app.run(debug=True)

db.create_all()
