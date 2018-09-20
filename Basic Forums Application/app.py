#importing flask
from flask import Flask, request, render_template, g, jsonify
import json
import sqlite3

app = Flask(__name__)

"""TODO:
       figure out how to initialize the DB and connect the rest of the time
       parse json
       insert data to json
       update data
"""

###### DATABASE SETUP SECTION ######

# Sets the path of the database
DATABASE = './data.db'

# Connects to the database
def get_db():
  db = getattr(g, '_database', None)
  if db is None:
       db = g._database = sqlite3.connect(DATABASE)
  return db

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

#initializes the data base using flask
def init_db():
  with app.app_context():
      db = get_db()
      with app.open_resource('init.sql', mode='r') as f:
          db.cursor().executescript(f.read())
      db.commit()
  print("*********************\nDATABASE INITALIZED\n*********************")

init_db()

def get_connections():
  conn = sqlite3.connect(DATABASE)
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur

###################################

#starting point to the flask app
@app.route("/")
def homePage():
    return "<h1>Test Page</h1>"

#triggered once the find forums button is pressed
@app.route("/forums/", methods=['GET','POST'])
def forums():
  con = get_gonnections()
  all_forums = con.execute('SELECT * FROM forums').fetchall()

  return jsonify(all_forums)

### NOT WORKING YET, STILL WORKING ON GETTING VARIABLE FROM URL
@app.route("/forums/<int:forum_id>", methods=['GET','POST'])
def threads():
  con = get_gonnections()
  all_forums = con.execute('SELECT * FROM forums').fetchall()

  return print(forum_id)

# if __name__ == "__main__":
  app.run(debug=True)