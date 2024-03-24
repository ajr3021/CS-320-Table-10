from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)   #
cors = CORS(app)    #
app.config['CORS_HEADERS'] = 'Content-Type' #

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
        
@app.route("/api/collection/<cid>")
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
#CURRENT ISSUE:
    #All of this code is untested.
    #TODO: Build unit tests, database simulator for testing the queries.

@app.route("/api/user/follow", method=['POST'])
@cross_origin(origins="*")
def follow_user(followerUid, followedUid):
    sql = f"INSERT INTO followers(followerId, followedId) VALUES ({followerUid}, {followedUid});"

    curs.execute(sql)   #Execute sql statement
    conn.commit()   #Commits change.
    #Returns tuple of empty array, status number.
    return {}, 200


@app.route("/api/user/follow", method=['DELETE'])
@cross_origin(origins="*")
def unfollow_user(followerUid, followedUid):
    sql = f"DELETE FROM followers WHERE followerId={followerUid} AND followedId={followedUid};"
    curs.execute(sql)   #Execute sql statement
    conn.commit()
    
    #Return tuple of list of users, status number.
    return {}, 200

@app.route("/api/user/follow", method=['GET'])
@cross_origin(origins="*")
def findByEmail(email):
    sql = f"SELECT name FROM users WHERE email={email};"

    curs.execute(sql)   #Execute sql statement
    result = curs.fetchall()
    conn.commit()
    #Return tuple of list of users, status.

    return result, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)