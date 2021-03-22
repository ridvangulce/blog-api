#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

api = Api()
app = Flask(__name__)
# -----------------------------------db-----------------------------------


db = SQLAlchemy(app)


def create_app():
    db.init_app(app)
    return app


engine = create_engine('mysql://root:password@localhost:3306')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def my_function():
    with app.app_context():
        user = db.User(...)
        db.session.add(user)
        db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


# -----------------------------------api-----------------------------------

users = [
    {
        'name': "Ridvan",
        'id': "1",
    },
    {
        'name': "Furkan",
        'id': "2",
    },
    {
        'name': "Vildan",
        'id': "3",
    },
    {
        'name': "Fatih",
        'id': "4",
    }
]


@app.route("/api", methods=['GET', 'POST'])
def api():
    return jsonify({"users": users})


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        id = request.form.get('id')

        return render_template("index.html", name=name, id=id)
    else:
        return render_template("index.html", error="Error!")
