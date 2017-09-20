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

if __name__ == '__main__':
    app.run()
