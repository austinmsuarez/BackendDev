from flask import Flask, request, render_template, g, jsonify,Response
from flask_basicauth import BasicAuth
import json
import sqlite3

app = Flask(__name__)

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

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource cannot be found.</p>", 404

#initializes the data base using flask
def init_db():
  with app.app_context():
      db = get_db()
      with app.open_resource('init.sql', mode='r') as f:
          db.cursor().executescript(f.read())
      db.commit()
  print("*********************\nDATABASE INITALIZED\n*********************")

#connects to DB
def get_connections():
  conn = sqlite3.connect(DATABASE)
  conn.row_factory = dict_factory
  cur = conn.cursor()
  return cur
###################################

###### VALIDATION SECTION ######

''' myAuthorizor:
    param: takes in BasicAuth
    uses:  used to override the check_credentials to check the Database 
           for authorized users
'''
class myAuthorizor(BasicAuth):
  def check_credentials(self, username, password):
    valid = False
    conn = get_connections()
    data = conn.execute('SELECT * FROM auth_users').fetchall()
    for entry in data:
      if entry["username"] == username and entry["password"] == password:
        valid = True
    return valid

def valid_username(newUsername):
  conn = get_connections()
  data = conn.execute('SELECT * FROM auth_users').fetchall()
  validNewUser = True
  for user in data:
    if user["username"] == newUsername:
      validNewUser = False
  return validNewUser


#checks for valid new Forum entry
def check_validForum(value):
  conn = get_connections()
  all_info = conn.execute('SELECT * FROM forums').fetchall()
  validNewForum = True
  for forum in all_info:
    if forum["name"] == value["name"]:
      validNewForum = False
  return validNewForum

###################################

#starting point to the flask app
@app.route("/")
def homePage():
    check_validForum("h")
    return "<h1>Test Page</h1>"


@app.route("/forums/", methods=['GET'])
def get_forums():
    con = get_connections()
    all_forums = con.execute('SELECT * FROM forums').fetchall()
    print(all_forums)
    return jsonify(all_forums)

@app.route("/forums/", methods=['POST'])
def post_forums():
  
  b_auth = myAuthorizor()
  db = get_db()
  db.row_factory = dict_factory
  conn = db.cursor()

  #pulls all forums and makes it to a json obj
  all_forums = conn.execute('SELECT * FROM forums').fetchall()
  req_data = request.get_json()
  
  #checks for valid forum entry
  if(check_validForum(req_data)):

    #gets input from user
    username = request.authorization['username']
    password = request.authorization['password']

    #checks to see if user has proper auth
    if b_auth.check_credentials(username, password):
      #inserts into the database
      forumName = req_data['name']
      conn.execute('INSERT INTO forums(name,creator) VALUES(\''+forumName+'\',\''+ username+'\')')
      db.commit()

      #returns a success response
      response = Response("HTTP 201 Created\n" + "Location header field set to /forums/<forum_id> for new forum.",201,mimetype = 'application/json')
      response.headers['Location'] = "/forums/" + forumName
    else:
      invalMsg = "User not authenticated"
      response = Response(invalMsg,409,mimetype = 'application/json')
  #if th conflict exisits return an error message
  else:
    invalMsg = "HTTP 409 Conflict if forum already exists"
    response = Response(invalMsg,409,mimetype = 'application/json')
  return response

''' TODO:
          create the post method
              check for a valid forum entry
              get timestamp for the post
              get author for the post
'''
@app.route("/forums/<forum_id>", methods=['GET','POST'])
def threads(forum_id):
  if request.method == 'POST':
    return None
  else:
    con = get_connections()
    query = 'SELECT * FROM threads WHERE forum_id=' + forum_id
    all_threads = con.execute(query).fetchall()
    if len(all_threads)==0:
        return page_not_found(404)
    else:
        return jsonify(all_threads)

'''TODO:
          create a GET for all posts
          create a POST for posts
'''
@app.route("/forums/<forum_id>/<thread_id>", methods=['GET','POST'])
def posts(forum_id, thread_id):
  if request.method == 'POST':
    return None
  else:
    con = get_connections()
    all_posts = con.execute('SELECT * FROM posts WHERE thread_id IN (SELECT id FROM threads WHERE id=' + thread_id + ' AND forum_id=' + forum_id + ')').fetchall()
    return jsonify(all_posts)


@app.route("/users", methods=['POST'])
def users():
    
    db = get_db()
    db.row_factory = dict_factory
    conn = db.cursor()

    req_data = request.get_json()
    newUser = req_data['username']
    newPass = req_data['password']

    if valid_username(newUser):
      conn.execute('INSERT INTO auth_users(username,password) VALUES(\''+newUser+'\',\''+ newPass+'\')')
      db.commit()
      #returns a success response
      response = Response("HTTP 201 Created",201,mimetype = 'application/json')
    else: 
      #returns a success response
      response = Response("HTTP 409 Conflict if username already exists\n",409,mimetype = 'application/json')
    return response

if __name__ == "__main__":
  init_db()
  app.run(debug=True)
