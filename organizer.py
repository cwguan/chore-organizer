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

    # Checks database to see if the apartmentName is already in use
    db_apartments = list(mongo.db.chores.find(
                                {"apartmentName" : session["apartmentName"]}))
    if len(db_apartments) != 0:
        return render_template('error_create.html', message = "Sorry, that name is \
                                already in use. Please use a different one.")

    # Handles user-input when numTasks is not an int or over the maximum
    try:
        session["numTasks"] = int(request.args["number-tasks"])
        maxTasks = 15
        if session["numTasks"] > maxTasks:
            return render_template('error_create.html', message = "Sorry, the current \
                                   maximum number of tasks right now is 15.")
    except ValueError:
        return render_template('error_create.html', message = "Sorry, something went \
                                wrong. Please enter an integer.")

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
    # Retrieves all the tasks user input using the same name attribute
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
    # Creates a dictionary with each task with a key of a list w/ every roommate
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
                                "task_nameList" : task_nameList
                                })
    session.clear()
    return redirect(url_for('renderFinish'))


@app.route('/finish')
def renderFinish():
    return render_template('finish.html')


@app.route('/create_restart')
def renderCreate_Restart():
    session.clear()
    return redirect(url_for('renderCreate'))


@app.route('/lookup')
def renderLookup():
    return render_template('lookup.html')


@app.route('/lookup2', methods=['GET', 'POST'])
def renderLookup2():
    inputName = request.form.get("apartmentName")
    inputPassword = request.form.get("password")

    # Finds the apartment that matches the name
    db_apartment = list(mongo.db.chores.find(
                         {"apartmentName" : inputName }))

    # Case 1: Could not find an apartment document that matches the name
    if len(db_apartment) == 0:
        return render_template('error_lookup.html', message = "Sorry, that \
                                apartment does not exist yet.")
    else:
        # Case 2: Password is incorrect for inputted apartment name
        if db_apartment[0]["password"] != inputPassword:
            return render_template('error_lookup.html', message = "Incorrect \
                                    password. Please try again.")
        # Case 3: Successful input, goes to the next step
        else:
            session["currentApartment"] = inputName
            return render_template('lookup2.html', apartment=db_apartment[0])


@app.route('/lookup3')
def renderLookup3():
    # Gathers info about the current roommate logging in & his/her apartment
    currentRoommate = request.args["current-roommate"]
    apartment = list(mongo.db.chores.find({"apartmentName" : session["currentApartment"] }))[0]

    # Iterates through the all the task-roommates to see if currentRoommate
    # is the zeroth index of any task
    assigned_tasks = []
    for task, roommate in apartment["task_nameList"].items():
        if roommate[0] == currentRoommate:
            assigned_tasks.append(task)

    # Case where the currentRoommate has no assigned tasks
    if len(assigned_tasks) == 0:
        session.clear()
        return render_template('lookup3.html', no_tasks=True)
    else:
        return render_template('lookup3.html', no_tasks=False,
                                currentRoommate=currentRoommate,
                                assigned_tasks=assigned_tasks)


@app.route('/finish_lookup', methods=['GET','POST'])
def renderFinish_Lookup():
    # List of all the tasks the currentRoommate has compeleted
    completed = request.form.getlist('finished-task')
    apartment = list(mongo.db.chores.find(
                         {"apartmentName": session["currentApartment"] }))[0]

    # For every completed task, pops that roommate's name and adds to the end
    for task in completed:
        tempName = apartment["task_nameList"][task].pop(0)
        apartment["task_nameList"][task].append(tempName)

    # Updates database key with the new task_nameList with pop/append
    mongo.db.chores.update({"apartmentName": session["currentApartment"]},
                            {
                                "$set":{"task_nameList": apartment["task_nameList"]}
                            })
    return render_template('finish_lookup.html', apartment=apartment)


@app.route('/lookup_restart')
def renderLookup_Restart():
    session.clear()
    return redirect(url_for('renderLookup'))


if __name__ == '__main__':
    app.run()
