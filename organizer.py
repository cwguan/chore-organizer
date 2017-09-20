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
    session[apartmentName] = request.args["apartment-name"]
    session[numRoommates] = int(request.args["number-roommates"])

    return redirect(url_for('renderCreate2'))

@app.route('/create2', methods=['GET', 'Post'])
def renderCreate2():
    return render_template('create2.html')

if __name__ == '__main__':
    app.run()
