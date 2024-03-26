from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)   #Creates flask application
cors = CORS(app)    #Enables Cross origin resource sharing (domain a can use stuff from domain b)
app.config['CORS_HEADERS'] = 'Content-Type' #??? Not sure

import os
from dotenv import load_dotenv

load_dotenv()   #Loads .env into OS environmental variables while process is running

import psycopg2
from sshtunnel import SSHTunnelForwarder
#Get from the OS environmental variables
username = os.environ.get('user')   #This should get the user from the .env file
password = os.environ.get('password')   #This should get the password from the .env file
dbName = "p320_10"  #Database name

server = SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432))    #SSH tunnel made between application and database.
server.start()  #Start the ssh tunnel
print("SSH tunnel established")
params = {
    'database': dbName,
    'user': username,
    'password': password,
    'host': 'localhost',
    'port': server.local_bind_port
}


conn = psycopg2.connect(**params)   #Create a connection object for the database with a given account.
curs = conn.cursor() # set up connection's ability to send commands.
print("Database connection established")

#index route
@app.route("/message") #The application route.
@cross_origin(origins="*")
def index():
    sql = "SELECT * FROM collection;"

    curs.execute(sql)
    result = curs.fetchall() 
    conn.commit()

    return result
        
@app.route("/api/collection/<cid>")#By default only GET requests are handled.
@cross_origin(origins="*")
def get_collection_by_id(cid):
    sql = f"SELECT * FROM collection WHERE cid={cid};"  #SQL DML statement to get all collections with a give cid.

    curs.execute(sql)   #Execute sql statement. return as: ???
    result = curs.fetchall() 
    conn.commit() #Commit database change.

    return result 

@app.route("/api/collection/<cid>", methods=['DELETE'])
@cross_origin(origins="*") #URL can be accessed from anywhere(?)
def delete_collection_by_id(cid):
    sql = f"DELETE FROM collection WHERE cid={cid};"    #SQL DML statement to remove a given collection.

    curs.execute(sql)  #Execute sql statement
    conn.commit() #Commit database change.

    return {}, 200
#STATE:
    #Backend urls respond properly
    #SQL statements should work in theory, tested them on a database simulation.
    #Tested the one statement that I wasn't sure about working.
@app.route("/api/user/follow", methods=['POST'])
@cross_origin(origins="*")
def follow_user():
    followerUid = int(request.args.get("followerUid"))
    followedUid = int(request.args.get("followedUid"))
    sql = f"INSERT INTO friends(uid, fid) VALUES ({followedUid}, {followerid});"
    print("followUser Called")
    curs.execute(sql)   #Execute sql statement
    conn.commit()   #Commits change.
    #Returns tuple of empty array, status number.
    return {}, 200


@app.route("/api/user/follow", methods=['DELETE'])
@cross_origin(origins="*")
def unfollow_user():
    followerUid = int(request.args.get("followerUid"))
    followedUid = int(request.args.get("followedUid"))
    sql = f"DELETE FROM friends WHERE fid={followerUid} AND uid={followedUid};"
    curs.execute(sql)   #Execute sql statement
    conn.commit()
    print("unfollowUser Called")
    #Return tuple of list of users, status number.
    return {}, 200

#Update API specification
#Use path parameters.
#email: Email fragment to search by
#uid:User ID. Ignored
@app.route("/api/user/follow/<uid>")#Only responds to GET
@cross_origin(origins="*")
def findByEmail(uid):
    #Get all users with an email containing some substring and is not already someone the user follows.
    #UI shouldn't allow user to follow themselves.
        #Get names where...
            #Get name from users where email fragment matches
            #the uid of the name of the person is not already followed by the user
    email = str(request.args.get("email"))
    
    sql = f"SELECT name, uid FROM player WHERE ( email LIKE \'{email}%\' ) AND ( uid NOT IN (SELECT (fid) FROM friends WHERE fid = {uid}) );"

    curs.execute(sql)   #Execute sql statement
    result = curs.fetchall()
    conn.commit() #Should probably be changed given problem with database transaction
    #Return tuple of list of users, status.
    #print("FindbyEmail Called")#Pass as form data
    return result, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)#Run on port 5050.