from flask import Flask, request
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

@app.route("/api/collection/collection/<cid>")
@cross_origin(origins="*")
def get_collection_by_id(cid):
    sql1 = f"SELECT cname FROM collection WHERE cid={cid};"

    curs.execute(sql1)
    collection_name = curs.fetchall()
    conn.commit()

    sql2 = f"""WITH IdList AS (SELECT vid FROM collection_has WHERE cid={cid}) SELECT i.vid, t1.title, t1.esrb_rating, t2.rating, t3.gameplay FROM IdList AS i
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
        gamedict["name"] = game[1]
        gamedict["esrb_rating"] = game[2]
        gamedict["rating"] = game[3]
        gameplay = game[4]
        if gameplay is None:
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
    sql = f"SELECT cname as name, COUNT(vg.vid) AS numGames, COALESCE(EXTRACT(EPOCH FROM SUM(endtime-starttime)/3600),0) as totalTimePlayed FROM collections_made LEFT JOIN collection ON collections_made.cid = collection.cid LEFT JOIN collection_has ON collection.CID = collection_has.CID LEFT JOIN video_game vg on collection_has.VID = vg.VID LEFT JOIN p320_10.gameplay g on vg.VID = g.vid WHERE collections_made.uid = {uid} GROUP BY collection.cid;"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    return result


@app.route("/api/videogame/", methods=['GET'])
@cross_origin(origins="*")
def get_random_videogame():
    game_sql = f"SELECT vid FROM video_game ORDER BY RANDOM() LIMIT 1;"
    curs.execute(game_sql)
    vid_sql = curs.fetchall()
    vid = vid_sql[0][0]

    gamedict = dict()
    title_sql = f"SELECT title FROM video_game WHERE vid = {vid};"
    curs.execute(title_sql)
    title = curs.fetchall()
    gamedict["title"] = title[0][0]

    esrb_sql = f"SELECT esrb_rating FROM video_game WHERE vid = {vid};"
    curs.execute(esrb_sql)
    esrb = curs.fetchall()
    gamedict["esrb_rating"] = esrb[0][0]

    rating_sql = f"SELECT AVG(rating) AS average_rating FROM Rates WHERE VID = {vid};"
    curs.execute(rating_sql)
    rating = curs.fetchall()
    gamedict["rating"] = rating[0][0]

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
    gamedict["platforms"] = temp2[0]
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


@app.route("/api/friends/<uid>", methods=['GET'])
@cross_origin(origins="*")
def get_friends(uid):
    sql = f"SELECT username FROM friends LEFT JOIN player ON friends.fid = player.uid WHERE friends.UID = {uid};"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    return result

@app.route("/api/collection/<cid>", methods=['PUT'])
@cross_origin(origins="*")
def change_collection_title_by_id(cid):
    title = request.form['title']
    sql = f"UPDATE collection SET cname='{title}' WHERE cid={cid};"

    curs.execute(sql)
    conn.commit()

    return title


@app.route("/api/collection/<cid>", methods=['DELETE'])
@cross_origin(origins="*")
def delete_collection_by_id(cid):
    sql = f"DELETE FROM collection WHERE cid={cid};"

    curs.execute(sql)
    conn.commit()

    return {}, 200


@app.route("/api/collection/<cid>/<vid>", methods=['POST'])
@cross_origin(origins="*")
def insert_videogame_into_collection(cid, vid):
    sql = f"INSERT INTO Collection_Has (CID, VID) VALUES ({cid}, {vid});"
    sql2 = f"SELECT * FROM video_game WHERE VID = {vid};"

    curs.execute(sql)
    curs.execute(sql2)
    result = curs.fetchall()
    conn.commit()

    return result


@app.route("/api/collection/<cid>/<vid>", methods=['DELETE'])
@cross_origin(origins="*")
def delete_videogame_from_collection(cid, vid):
    sql = f"DELETE FROM Collection_Has WHERE CID = {cid} and VID = {vid};"

    curs.execute(sql)
    conn.commit()

    return {}, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
