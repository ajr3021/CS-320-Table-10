from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone

# (imports requiered for data entry. Source files do not exist on git)
# import Data.data_loader as dl
# import pandas as pd

app = Flask(__name__)  # Creates flask application
cors = CORS(app)  # Enables Cross origin resource sharing (domain a can use stuff from domain b)
app.config['CORS_HEADERS'] = 'Content-Type'  # ??? Not sure

import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env into OS environmental variables while process is running

import psycopg2
from sshtunnel import SSHTunnelForwarder

bcrypt = Bcrypt(app)

LOGGED_IN_USER_ID = 1

username = os.environ.get('user')
password = os.environ.get('password')
dbName = "p320_10"

server = SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=(
                            '127.0.0.1', 5432))  # SSH tunnel made between application and database.
server.start()  # Start the ssh tunnel
print("SSH tunnel established")
params = {
    'database': dbName,
    'user': username,
    'password': password,
    'host': 'localhost',
    'port': server.local_bind_port
}

conn = psycopg2.connect(**params)  # Create a connection object for the database with a given account.
curs = conn.cursor()  # set up connection's ability to send commands.
print("Database connection established")


# To add data into the database using python. (The package being used is not on git)
# df = pd.DataFrame({'gid': [11], 'gname': ['test']})
# dl.dataframe_to_postgres(conn, curs, df, 'genre')


# index route
@app.route("/message")  # The application route.
@cross_origin(origins="*")
def index():
    sql = "SELECT * FROM collection;"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    return result


@app.route("/api/signup", methods=["POST"])
@cross_origin(origins="*")
def signup():
    data = request.get_json(force=True)

    username = data['username']
    password = data['password']
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']

    sql = "SELECT COUNT(*) from player"


@app.route("/api/login", methods=["POST"])
@cross_origin(origins="*")
def login():
    global LOGGED_IN_USER_ID
    data = request.get_json(force=True)

    username = data['username']
    password = data['password']

    sql = f"SELECT password, uid FROM player WHERE username='{username}';"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    hashed_password = result[0][0]

    is_valid = bcrypt.check_password_hash(hashed_password, password)

    if is_valid:
        LOGGED_IN_USER_ID = result[0][1]
        return {}, 200
    return {}, 201


@app.route("/api/collection/<cid>")  # By default only GET requests are handled.
@cross_origin(origins="*")
def get_collection_by_id(cid):
    sql1 = f"SELECT cname FROM collection WHERE cid={cid};"

    curs.execute(sql1)
    collection_name = curs.fetchall()
    conn.commit()

    sql2 = f"""WITH IdList AS (SELECT vid FROM collection_has WHERE cid={cid}) SELECT i.vid, t1.title, t1.esrb_rating, t2.rating, t3.gameplay, t1.description, t1.image FROM IdList AS i
        LEFT JOIN video_game AS t1 ON t1.vid = i.vid
        LEFT JOIN (SELECT vid, AVG(rating) as rating FROM rates GROUP BY vid) AS t2 ON t2.vid = i.vid
        LEFT JOIN (SELECT vid, EXTRACT(EPOCH FROM SUM(endtime-starttime))/3600 AS gameplay FROM gameplay GROUP BY vid) AS t3 ON t3.vid = i.vid;"""

    curs.execute(sql2)
    games = curs.fetchall()
    conn.commit()

    gamelist = list()
    for game in games:
        gamedict = dict()
        vid = game[0]
        gamedict["vid"] = int(vid)
        gamedict["name"] = game[1]
        gamedict["esrb_rating"] = game[2]
        gamedict["rating"] = int(game[3])

        gameplay = game[4]

        gamedict["description"] = game[5]
        gamedict["banner"] = game[6]

        if gameplay is None:
            gameplay = 0
        gamedict["gameplay"] = int(gameplay)
        # get genres for the game
        genre_sql = f"SELECT gname FROM has_genre LEFT JOIN genre ON has_genre.GID = genre.GID WHERE vid={vid};"
        curs.execute(genre_sql)
        temp = curs.fetchall()
        temp2 = []
        for lst in temp:
            temp2.append(lst[0])
        gamedict["genres"] = temp2
        # get the platforms the game is on
        platform_sql = f"SELECT pname, price FROM game_platform LEFT JOIN platform ON game_platform.pid = platform.pid WHERE vid={vid};"
        curs.execute(platform_sql)
        temp = curs.fetchall()
        temp2 = []
        for item in temp:
            newdict = dict()
            newdict["platform"] = item[0]
            newdict["price"] = item[1]
            gamedict["price"] = item[1]
            temp2.append(newdict)
        gamedict["platforms"] = temp2
        # get the developers of the game
        developer_sql = f"SELECT sname FROM development LEFT JOIN studio ON development.sid = studio.sid WHERE vid={vid};"
        curs.execute(developer_sql)
        temp = curs.fetchall()
        temp2 = []
        for lst in temp:
            temp2.append(lst[0])
        gamedict["developers"] = temp2
        gamelist.append(gamedict)

    result3 = {
        "name": collection_name[0][0],
        "games": gamelist
    }
    return result3


# tested ^

@app.route("/api/collection/user/<uid>")
@cross_origin(origins="*")
def get_collection_by_user(uid):
    sql = f"SELECT collection.cid, cname as name, COUNT(vg.vid) AS numGames, COALESCE(EXTRACT(EPOCH FROM SUM(endtime-starttime)/3600),0) as totalTimePlayed FROM collections_made LEFT JOIN collection ON collections_made.cid = collection.cid LEFT JOIN collection_has ON collection.CID = collection_has.CID LEFT JOIN video_game vg on collection_has.VID = vg.VID LEFT JOIN p320_10.gameplay g on vg.VID = g.vid WHERE collections_made.uid={uid} GROUP BY collection.cid;"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    print(result)

    final_result = []

    for i in range(len(result)):
        final_result.append({
            "cid": result[i][0],
            "name": result[i][1],
            "numGames": result[i][2],
            "totalTimePlayed": result[i][3]
        })

    print(final_result)

    return final_result


@app.route("/api/collection/user")
@cross_origin(origins="*")
def get_collection_by_current_user():
    sql = f"SELECT collection.cid, cname as name, COUNT(vg.vid) AS numGames, COALESCE(EXTRACT(EPOCH FROM SUM(endtime-starttime)/3600),0) as totalTimePlayed FROM collections_made LEFT JOIN collection ON collections_made.cid = collection.cid LEFT JOIN collection_has ON collection.CID = collection_has.CID LEFT JOIN video_game vg on collection_has.VID = vg.VID LEFT JOIN p320_10.gameplay g on vg.VID = g.vid WHERE collections_made.uid = {LOGGED_IN_USER_ID} GROUP BY collection.cid;"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    final_result = []

    for i in range(len(result)):
        final_result.append({
            "cid": result[i][0],
            "name": result[i][1],
            "numGames": result[i][2],
            "totalTimePlayed": result[i][3]
        })

    return final_result


@app.route("/api/videogame/", methods=['GET'])
@cross_origin(origins="*")
def get_random_videogame():
    game_sql = f"SELECT vid FROM video_game ORDER BY RANDOM() LIMIT 1;"
    curs.execute(game_sql)
    vid_sql = curs.fetchall()
    vid = vid_sql[0][0]

    gamedict = dict()

    gamedict["vid"] = vid

    title_sql = f"SELECT title FROM video_game WHERE vid = {vid};"
    curs.execute(title_sql)
    title = curs.fetchall()
    gamedict["title"] = title[0][0]

    description_sql = f"SELECT description FROM video_game WHERE vid = {vid};"
    curs.execute(description_sql)
    description = curs.fetchall()
    gamedict["description"] = description[0][0]

    image_sql = f"SELECT image FROM video_game WHERE vid = {vid};"
    curs.execute(image_sql)
    image = curs.fetchall()
    gamedict["banner"] = image[0][0]

    esrb_sql = f"SELECT esrb_rating FROM video_game WHERE vid = {vid};"
    curs.execute(esrb_sql)
    esrb = curs.fetchall()
    gamedict["esrb_rating"] = esrb[0][0]

    rating_sql = f"SELECT AVG(rating) AS average_rating FROM Rates WHERE VID = {vid};"
    curs.execute(rating_sql)
    rating = curs.fetchall()
    gamedict["rating"] = int(rating[0][0])

    gameplay_sql = f"SELECT EXTRACT(EPOCH FROM SUM(endtime-starttime))/3600 AS total_hours from gameplay where vid={vid} GROUP BY vid;"
    curs.execute(gameplay_sql)
    gameplay = curs.fetchall()
    if gameplay == []:
        gameplay = 0
    gamedict["gameplay"] = gameplay

    # get genres for the game
    genre_sql = f"SELECT gname FROM has_genre LEFT JOIN genre ON has_genre.GID = genre.GID WHERE vid={vid};"
    curs.execute(genre_sql)
    temp = curs.fetchall()
    temp2 = []
    for lst in temp:
        temp2.append(lst[0])
    gamedict["genres"] = temp2
    # get the platforms the game is on
    platform_sql = f"SELECT pname, price FROM game_platform LEFT JOIN platform ON game_platform.pid = platform.pid WHERE vid={vid};"
    curs.execute(platform_sql)
    temp = curs.fetchall()
    temp2 = []
    for item in temp:
        newdict = dict()
        newdict["platform"] = item[0]
        newdict["price"] = item[1]
        temp2.append(newdict)
    gamedict["platforms"] = temp2
    # get the developers of the game
    developer_sql = f"SELECT sname FROM development LEFT JOIN studio ON development.sid = studio.sid WHERE vid={vid};"
    curs.execute(developer_sql)
    temp = curs.fetchall()
    temp2 = []
    for item in temp:
        gamedict["price"] = item[1]
        temp2.append(item[0])
    gamedict["developers"] = temp2

    conn.commit()

    return gamedict


@app.route("/api/videogame/<vid>", methods=['GET'])
@cross_origin(origins="*")
def get_videogame_by_id(vid):
    gamedict = dict()

    gamedict["vid"] = vid

    title_sql = f"SELECT title FROM video_game WHERE vid = {vid};"
    curs.execute(title_sql)
    title = curs.fetchall()
    gamedict["title"] = title[0][0]

    description_sql = f"SELECT description FROM video_game WHERE vid = {vid};"
    curs.execute(description_sql)
    description = curs.fetchall()
    gamedict["description"] = description[0][0]

    image_sql = f"SELECT image FROM video_game WHERE vid = {vid};"
    curs.execute(image_sql)
    image = curs.fetchall()
    gamedict["banner"] = image[0][0]

    esrb_sql = f"SELECT esrb_rating FROM video_game WHERE vid = {vid};"
    curs.execute(esrb_sql)
    esrb = curs.fetchall()
    gamedict["esrb_rating"] = esrb[0][0]

    rating_sql = f"SELECT AVG(rating) AS average_rating FROM Rates WHERE VID = {vid};"
    curs.execute(rating_sql)
    rating = curs.fetchall()
    gamedict["rating"] = int(rating[0][0])

    gameplay_sql = f"SELECT EXTRACT(EPOCH FROM SUM(endtime-starttime))/3600 AS total_hours from gameplay where vid={vid} GROUP BY vid;"
    curs.execute(gameplay_sql)
    gameplay = curs.fetchall()
    if gameplay == []:
        gameplay = 0
    gamedict["gameplay"] = gameplay

    # get genres for the game
    genre_sql = f"SELECT gname FROM has_genre LEFT JOIN genre ON has_genre.GID = genre.GID WHERE vid={vid};"
    curs.execute(genre_sql)
    temp = curs.fetchall()
    temp2 = []
    for lst in temp:
        temp2.append(lst[0])
    gamedict["genres"] = temp2
    # get the platforms the game is on
    platform_sql = f"SELECT pname, price FROM game_platform LEFT JOIN platform ON game_platform.pid = platform.pid WHERE vid={vid};"
    curs.execute(platform_sql)
    temp = curs.fetchall()
    temp2 = []
    for item in temp:
        gamedict["price"] = item[1]
        temp2.append(item[0])
    gamedict["platforms"] = temp2
    # get the developers of the game
    developer_sql = f"SELECT sname FROM development LEFT JOIN studio ON development.sid = studio.sid WHERE vid={vid};"
    curs.execute(developer_sql)
    temp = curs.fetchall()
    temp2 = []
    for lst in temp:
        temp2.append(lst[0])
    gamedict["developers"] = temp2

    conn.commit()

    return gamedict

@app.route("/api/friends", methods=['GET'])
@cross_origin(origins="*")
def get_friends():
    sql = f"SELECT username, email FROM friends LEFT JOIN player ON friends.fid = player.uid WHERE friends.UID = {LOGGED_IN_USER_ID};"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    print(result)

    final_result = []

    for i in range(len(result)):
        final_result.append({
            "username": result[i][0],
            "email": result[i][1]
        })

    return final_result


@app.route("/api/collection/<cid>", methods=['PUT'])
@cross_origin(origins="*")
def change_collection_title_by_id(cid):
    data = request.get_json(force=True)

    title = data['title']
    sql = f"UPDATE collection SET cname='{title}' WHERE cid={cid};"

    curs.execute(sql)
    conn.commit()

    return title


@app.route("/api/collection/<cid>", methods=['DELETE'])
@cross_origin(origins="*")  # URL can be accessed from anywhere(?)
def delete_collection_by_id(cid):
    sql = f"DELETE FROM collection WHERE cid={cid};"  # SQL DML statement to remove a given collection.

    curs.execute(sql)  # Execute sql statement
    conn.commit()  # Commit database change.

    return {}, 200


# STATE:
# Backend urls respond properly
# SQL statements should work in theory, tested them on a database simulation.
# Tested the one statement that I wasn't sure about working.

@app.route("/api/user/follow/<uid>", methods=['POST'])
@cross_origin(origins="*")
def follow_user():
    data = request.get_json(force=True)
    followerUid = int(data["followerUid"])#Get all external data from parameters.
    followedUid = int(data["followedUid"])
    sql = f"INSERT INTO friends(uid, fid) VALUES ({followedUid}, {followerid});"
    curs.execute(sql)   #Execute sql statement
    conn.commit()   #Commits change.
    #Returns tuple of empty array, status number.
    return {}, 200


@app.route("/api/user/follow/<uid>", methods=['DELETE'])
@cross_origin(origins="*")
def unfollow_user(uid):
    sql = f"DELETE FROM friends WHERE uid={LOGGED_IN_USER_ID} AND fid={uid};"
    curs.execute(sql)  # Execute sql statement
    conn.commit()
    print("unfollowUser Called")
    # Return tuple of list of users, status number.
    return {}, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
