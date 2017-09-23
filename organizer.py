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

    # Handles user-input when it is not an int or when it is over the maximum
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


@app.route('/create4')
def renderCreate4():
    session["tasks"] = request.args.getlist('tasks')
    return render_template('create4.html', names=session["names"],
                            tasks=session["tasks"], numTasks=session["numTasks"])


@app.route('/create5')
def renderCreate5():
    assignments = request.args.getlist('task-roommate')
    # Creates a dictionary where the task is the key, roommate is the value
    task_roommate = {}
    index = 0
    for item in session["tasks"]:
        # Uses list from create4 and iterates through in order
        task_roommate[item] = assignments[index]
        index += 1

    # Saves dictionary to session
    session["task-roommate"] = task_roommate
    return render_template('create5.html', names=session["names"],
                            tasks=session["tasks"], numTasks=session["numTasks"],
                            task_roommate=session["task-roommate"])


@app.route('/save_result')
def renderSave_Result():
    # Creates a dictionary with each task and a list of every roommate
    task_nameList = {}
    for task in session["tasks"]:
        # List to hold the person first assigned to a task, then the rest
        tempList=[]
        tempList.append(session["task-roommate"][task])

        # Iterates through remaining names & adds to the list
        for name in session["names"]:
            if name != tempList[0]:
                tempList.append(name)

        task_nameList[task] = tempList

    # Saves information from session to database and clears the session
    mongo.db.chores.insert_one({"apartmentName" : session["apartmentName"],
                                "password" : session["password"],
                                "numRoommates" : session["numRoommates"],
                                "names" : session["names"],
                                "numTasks" : session["numTasks"],
                                "tasks" : session["tasks"],
                                "task-nameList" : task_nameList
                                })
    session.clear()
    return redirect(url_for('renderFinish'))


@app.route('/finish')
def renderFinish():
    return render_template('finish.html')


if __name__ == '__main__':
    app.run()
