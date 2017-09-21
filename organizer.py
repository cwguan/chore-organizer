from flask import Flask, redirect, url_for, session, request, jsonify
from flask_pymongo import PyMongo
from flask import render_template, flash, Markup

import pprint
import os
import sys
import traceback

app = Flask(__name__)
app.debug = False
app.secret_key = os.environ['APP_SECRET_KEY']

# Configures correct environmental variables for MongoDB with mLab
app.config['MONGO_HOST'] = os.environ['MONGO_HOST']
app.config['MONGO_PORT'] = int(os.environ['MONGO_PORT'])
app.config['MONGO_DBNAME'] = os.environ['MONGO_DBNAME']
app.config['MONGO_USERNAME'] = os.environ['MONGO_USERNAME']
app.config['MONGO_PASSWORD'] = os.environ['MONGO_PASSWORD']
mongo = PyMongo(app)

#mongo.db.chores.insert_one()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create')
def renderCreate():
    return render_template('create.html')


@app.route('/create_result', methods=['GET', 'POST'])
def renderCreate_Result():
    # Retrieves the information from the form and stores it in the session
    session["apartmentName"] = request.args["apartment-name"]
    session["password"] = request.args["password"]
    session["numRoommates"] = int(request.args["number-roommates"])

    ''' CHECK IN DATABASE IF NAME/PASSWORD ALREADY IN USE'''

    # Handles user-input when it is not an int
    try:
        session["numTasks"] = int(request.args["number-tasks"])
        maxTasks = 15
        if session["numTasks"] > maxTasks:
            return "Sorry, the current maximum number of tasks right now is 15."
    except ValueError:
        return "Sorry, something went wrong. Please enter an integer."

    return redirect(url_for('renderCreate2'))


@app.route('/create2')
def renderCreate2():
    return render_template('create2.html', numRoommates=session["numRoommates"])


@app.route('/create3', methods=['GET', 'POST'])
def renderCreate3():
    # Retrieves list using input tags that share the same name attribute
    session["names"] = request.args.getlist('names')
    return render_template('create3.html', names=session["names"], numTasks=session["numTasks"])


if __name__ == '__main__':
    app.run()
