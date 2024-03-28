from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from sshtunnel import SSHTunnelForwarder

username = os.environ.get('user')
password = os.environ.get('password')
dbName = "p320_10"

server = SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432))
server.start()
print("SSH tunnel established")
params = {
    'database': dbName,
    'user': username,
    'password': password,
    'host': 'localhost',
    'port': server.local_bind_port
}


conn = psycopg2.connect(**params)
curs = conn.cursor()
print("Database connection established")

#index route
@app.route("/message")
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
    sql = f"SELECT * FROM collection WHERE cid={cid};"

    curs.execute(sql)
    result = curs.fetchall() 
    conn.commit()

    return result 

@app.route("/api/collection/<cid>", methods=['DELETE'])
@cross_origin(origins="*")
def delete_collection_by_id(cid):
    sql = f"DELETE FROM collection WHERE cid={cid};"

    curs.execute(sql)
    conn.commit()

    return {}, 200
@app.route("/api/videogame/<vid>", methods=['GET'])
@cross_origin(origins="*")
def getGame(vid):
    sql = f"SELECT * FROM video_game WHERE vid={vid};"

    curs.execute(sql)
    result = curs.fetchall()#This should always be of size one. Otherwise database has an issue.
    conn.commit()

    return result, 200
#Use route parameters. Why not? May change in the future.
@app.route("/api/videogame/<vid>", methods=['POST'])
@cross_origin(origins="*")
def makeGame(vid):
    vid = int(vid)
    title = str(request.args.get("title"))#Get all external data from parameters.
    esrb = str(request.args.get("esrb_rating"))
    image = str(request.args.get("image"))
    desc = str(request.args.get("description"))
    sql = f"INSERT INTO video_game(vid, esb_rating, title, image, description) VALUES ({vid}, {esrb}, {title}, {image}, {desc});"

    curs.execute(sql)
    conn.commit()

    return 200

@app.route("/api/videogame/<uid>/<vid>", methods=['POST'])
@cross_origin(origins="*")
def addPlaytime(uid, vid):
    pass

#WIP function. Comment out if needed.
#seachBy:The attribute to seach for: name, platform, release date, developers, price, or genre.
#sortBy:Ascending or descending
#data:The data to look at
#Row:video game’s name, platforms, the developers, the publisher, the playtime (of user) and the esrb and aggregate user ratings.
@app.route("/api/videogame/<uid>/<searchBy>/<sortBy>/<data>", methods=['GET'])
@cross_origin(origins="*")
def searchAndSortGames(uid, searchBy, sortBy, data):
    #assume the data is correct.

    #Prevent unwanted sql statements.
    if sortBy != "DESC" and sortBy != "ASC":
        return {}, 400
    #For this statement I'm gonna need to join multiple tables together to get all the data I need.
    #Sort alphabetically and release date-wise ascending
    #Tables used:
        #video_game (name, esrb rating)
        #game_platform (needed to get price, release_date)
        #Gameplay (for that of user)
        #publishing (for publishers)
        #development (needed to get all developers of a game)
        #rates (needed to get average of all user ratings)
    #Development and publishing are BOTH going to be arrays. I could get them in a separate sql query and return a new list of resulting tuples(?)
    sql = f"SELECT title FROM video_game WHERE {searchBy}={data} ORDER BY title ASC, ;"

    curs.execute(sql)
    conn.commit()
    return result, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)