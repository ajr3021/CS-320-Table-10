from flask import Flask
from flask import request
from flask import Flask, request
from flask_cors import CORS, cross_origin
import datetime
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
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
#Finished all of the first draft code.
    #Need to test all methods.
        #Test if the routes and param structure works correctly
        #Test the individual sql statements.

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

#
# LOGIN ROUTES
#
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

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    uid = result[0][0] + 1

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    dt = datetime.now(timezone.utc)

    sql = f"INSERT INTO player (uid, username, password, firstname, lastname, lastaccessdate, email, creationdate) VALUES('{uid}','{username}', '{hashed_password}', '{firstname}', '{lastname}', '{dt}', '{email}', '{dt}');"

    curs.execute(sql)
    conn.commit()

    return result


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


#
# COLLECTION ROUTES
#

@app.route("/api/collection", methods=['POST'])
@cross_origin(origins="*")
def create_empty_collection():
    sql = "SELECT COUNT(*) from collection"

    curs.execute(sql)
    result = curs.fetchall() 
    conn.commit()

    cid = int(result[0][0]) * 100 + 1

    data = request.get_json(force=True)

    name = data['name']

    sql = f"INSERT INTO collection (cid, cname) VALUES('{cid}','{name}');"

    curs.execute(sql)
    conn.commit()

    sql = f"INSERT INTO collections_made (cid, uid) VALUES('{cid}','{LOGGED_IN_USER_ID}');"

    curs.execute(sql)
    conn.commit()

    return {"cid": cid}, 200


@app.route("/api/collection/<cid>", methods=['GET'])  # By default only GET requests are handled.
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
        if game[3] is not None:
            gamedict["rating"] = int(game[3])
        else:
            gamedict["rating"] = 0

        try:
            gameplay = game[4]
        except:
            gameplay = 0

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

    try:
        result3 = {
            "name": collection_name[0][0],
            "games": gamelist
        }
    except:
        return {}, 200
    return result3


# tested ^

@app.route("/api/collection/user", methods=['GET'])
@cross_origin(origins="*")
def get_collection_by_user():
    sql = f"SELECT collection.cid, cname as name, COUNT(vg.vid) AS numGames, COALESCE(EXTRACT(EPOCH FROM SUM(endtime-starttime)/3600),0) as totalTimePlayed FROM collections_made LEFT JOIN collection ON collections_made.cid = collection.cid LEFT JOIN collection_has ON collection.CID = collection_has.CID LEFT JOIN video_game vg on collection_has.VID = vg.VID LEFT JOIN p320_10.gameplay g on vg.VID = g.vid WHERE collections_made.uid={LOGGED_IN_USER_ID} GROUP BY collection.cid ORDER BY cname;"

    curs.execute(sql)
    try:
        result = curs.fetchall()
    except:
        result = []
    conn.commit()

    print(result)

    final_result = []

    try:

        for i in range(len(result)):
            final_result.append({
                "cid": result[i][0],
                "name": result[i][1],
                "numGames": result[i][2],
                "totalTimePlayed": result[i][3]
            })
    except:
        pass

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

@app.route("/api/rating/<vid>/<data>", methods=['POST'])
@cross_origin(origins="*")
def rate_videogame(vid, data):
    rating = int(data)
    sql = f"INSERT INTO rates (uid, vid, rating) VALUES ({LOGGED_IN_USER_ID}, {vid}, {rating})"

    curs.execute(sql)
    conn.commit()

    return {}, 200



@app.route("/api/collection/<cid>/<vid>", methods=['POST'])
@cross_origin(origins="*")
def insert_videogame_into_collection(cid,vid):
    sql=f"INSERT INTO Collection_Has (CID,VID) VALUES ({cid},{vid});"
    sql2=f"SELECT * FROM video_game WHERE VID = {vid};"

    curs.execute(sql)
    curs.execute(sql2)
    result = curs.fetchall()
    conn.commit()

    return result


@app.route("/api/collection/<cid>/<vid>",methods=['DELETE'])
@cross_origin(origins="*")
def delete_videogame_from_collection(cid,vid):
    sql=f"DELETE FROM Collection_Has WHERE CID = {cid} and VID = {vid};"

    curs.execute(sql)
    conn.commit()

    return{},200


@app.route("/api/collection/<cid>", methods=['DELETE'])
@cross_origin(origins="*")  # URL can be accessed from anywhere(?)
def delete_collection_by_id(cid):
    sql = f"DELETE FROM collection WHERE cid={cid};"  # SQL DML statement to remove a given collection.

    curs.execute(sql)  # Execute sql statement
    conn.commit()  # Commit database change.

    return {}, 200


@app.route("/api/collection/<cid>", methods=['PUT'])
@cross_origin(origins="*")
def change_collection_title_by_id(cid):
    data = request.get_json(force=True)

    title = data['title']
    sql = f"UPDATE collection SET cname='{title}' WHERE cid={cid};"

    curs.execute(sql)
    conn.commit()

    return title

#
# VIDEO GAME ROUTES
# missing: /videogame/{vid} (POST), /videogame search sort, /videogame/{vid}/play (POST)
#
@app.route("/api/videogame/collection/<cid>", methods=['GET'])
@cross_origin(origins="*")
def get_random_videogame(cid):
    game_sql = f"SELECT vid FROM collection_has WHERE cid={cid} ORDER BY RANDOM() LIMIT 1;"
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
    print(title)
    if title is not None and title != []:
        gamedict["title"] = title[0][0]

    description_sql = f"SELECT description FROM video_game WHERE vid = {vid};"
    curs.execute(description_sql)
    description = curs.fetchall()
    if description is not None and description != []:
        gamedict["description"] = description[0][0]

    image_sql = f"SELECT image FROM video_game WHERE vid = {vid};"
    curs.execute(image_sql)
    image = curs.fetchall()
    if image is not None and image != []:
        gamedict["banner"] = image[0][0]

    esrb_sql = f"SELECT esrb_rating FROM video_game WHERE vid = {vid};"
    curs.execute(esrb_sql)
    esrb = curs.fetchall()
    if esrb is not None and esrb != []:
        gamedict["esrb_rating"] = esrb[0][0]

    rating_sql = f"SELECT AVG(rating) AS average_rating FROM Rates WHERE vid = {vid};"
    curs.execute(rating_sql)
    rating = curs.fetchall()

    gamedict["rating"] = 0

    print(rating)
    if rating is not None and rating[0][0] is not None:
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


#Formatted Data: '23:19'
#THIS WORKS!!
@app.route("/api/videogame/<uid>/<vid>", methods=['POST'])
@cross_origin(origins="*")
def addPlaytime(uid, vid):
    sTime = str(request.args.get("starttime"))
    sTimeNumbers = sTime.split(':')

    startTime = datetime.datetime.now()
    startTime = startTime.replace(hour = int(sTimeNumbers[0]),minute = int(sTimeNumbers[1]))

    eTime = str(request.args.get("endtime"))
    eTimeNumbers = eTime.split(':')

    endTime = datetime.datetime.now()
    endTime = endTime.replace(hour = int(eTimeNumbers[0]),minute = int(eTimeNumbers[1]))

    sql = "INSERT INTO gameplay(uid, vid, starttime, endtime) VALUES (%s, %s, %s, %s);"

    curs.execute(sql, (uid, vid, startTime, endTime))#We can change this from format string to data later.
    conn.commit()
    return {}, 200


@app.route("/api/videogame/<vid>", methods=['GET'])
@cross_origin(origins="*")
def getGame(vid):
    sql = "SELECT * FROM video_game WHERE vid=%s;"

    curs.execute(sql, (vid,))
    result = curs.fetchall() #This should always be of size one. Otherwise database has an issue.
    conn.commit()

    return result, 200


#Use route parameters. Why not? May change in the future.
#THIS WORKS!!
@app.route("/api/videogame/<vid>", methods=['POST'])
@cross_origin(origins="*")
def makeGame(vid):
    vid = str(vid)
    title = str(request.args.get("title"))#Get all external data from parameters.
    esrb = str(request.args.get("esrb_rating"))
    image = str(request.args.get("image"))
    desc = str(request.args.get("description"))
    #Works
    sql = "INSERT INTO video_game(vid, esrb_rating, title, image, description) VALUES (%s, %s, %s, %s, %s);"
    #Function below works. vid gets converted.
    curs.execute(sql, (vid, esrb, title, image, desc))
    conn.commit()

    return {}, 200

#
# USER ROUTES
#
@app.route("/api/friends", methods=['GET'])
@cross_origin(origins="*")
def get_friends():
    sql = f"SELECT username, email, player.uid FROM friends LEFT JOIN player ON friends.fid = player.uid WHERE friends.UID = {LOGGED_IN_USER_ID};"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    print(result)

    final_result = []

    for i in range(len(result)):
        final_result.append({
            "username": result[i][0],
            "email": result[i][1],
            "uid": result[i][2]
        })

    return final_result


# STATE:
# Backend urls respond properly
# SQL statements should work in theory, tested them on a database simulation.
# Tested the one statement that I wasn't sure about working.

@app.route("/api/user/follow/<uid>", methods=['POST'])
@cross_origin(origins="*")
def follow_user(uid):
    sql = f"INSERT INTO friends(uid, fid) VALUES ({LOGGED_IN_USER_ID}, {uid});"
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
    # Return tuple of list of users, status number.
    return {}, 200

#Update API specification
#Use path parameters.
#email: Email fragment to search by
#uid:User ID. Ignored
@app.route("/api/user/follow/<email>")#Only responds to GET
@cross_origin(origins="*")
def findByEmail(email):
    #Get all users with an email containing some substring and is not already someone the user follows.
    #UI shouldn't allow user to follow themselves.
        #Get names where...
            #Get name from users where email fragment matches
            #the uid of the name of the person is not already followed by the user
    #Statement
    sql = f"SELECT x.username, x.email, x.uid FROM (SELECT username, email, uid FROM player WHERE ( email LIKE \'{email}%\' ) AND uid NOT IN (SELECT uid FROM friends WHERE fid = {LOGGED_IN_USER_ID}) ) as x WHERE uid != {LOGGED_IN_USER_ID};"

    curs.execute(sql)   #Execute sql statement
    result = curs.fetchall()
    conn.commit() #Should probably be changed given problem with database transaction

    final_result = []

    for i in range(len(result)):
        final_result.append({
            "username": result[i][0],
            "email": result[i][1],
            "uid": result[i][2]
        })

    #Return tuple of list of users, status.
    #print("FindbyEmail Called")#Pass as form data
    return final_result


#WIP function. Comment out if needed.
#seachBy:The attribute to seach for: name, platform, release date, developers, price, or genre.
#sortBy:Ascending or descending
#data:The data to look at
#Row:video game’s name, platforms, the developers, the publisher, the playtime (of user) and the esrb and aggregate user ratings.
#Not properly tested
@app.route("/api/videogame/<uid>/<searchBy>/<data>", methods=['GET'])
@cross_origin(origins="*")
def searchAndSortGames(uid, searchBy, data):
    #assume the data is correct.

    #Prevent unwanted sql statements.
    if searchBy == "title":
        subQuery = f"{searchBy}=\'{data}%\'"
    elif searchBy == "pname":
        subQuery = f"gp.pid IN (SELECT platform.pid FROM (game_platform INNER JOIN platform ON platform.pid = game_platform.pid) WHERE pname = \'{data}%\')"
    elif searchBy == "developer":
        subQuery = f"vg.vid IN (SELECT development.vid FROM (development INNER JOIN studio ON development.sid = studio.sid) WHERE studio.sname = \'{data}%\')"
    elif searchBy == "price":
        subQuery =  f"{searchBy}={data}"
    elif searchBy == "genre":
        subQuery =  f"vg.vid IN (SELECT vid FROM (has_genre INNER JOIN genre on genre.gid = has_genre.gid) WHERE gname = \'{data}\' )"
    else:
        return {}, 400
    mainQuery = f"SELECT DISTINCT vg.vid as vid, vg.title as title, gp.release_date as rDate FROM (video_game vg INNER JOIN game_platform gp ON vg.vid = gp.vid) WHERE " + subQuery + " ORDER BY vg.title, gp.release_date;"
    #Get all the vids that fulfill the sort and search requirements
    games_results = []
    curs.execute(mainQuery)
    conn.commit()
    game_list = curs.fetchall()#This should fetch tuples of title and vid
    for gameId in game_list:
        print(str(gameId[0]))
        print(type(str(gameId[0])))
        game_name_sql = f"SELECT title FROM video_game WHERE vid={gameId[0]};"
        curs.execute(game_name_sql)
        conn.commit()
        game_name = curs.fetchone()

        game_desc_sql = f"SELECT description FROM video_game WHERE vid={gameId[0]};"
        curs.execute(game_desc_sql)
        conn.commit()
        game_desc = curs.fetchone()

        game_image_sql = f"SELECT image FROM video_game WHERE vid={gameId[0]};"
        curs.execute(game_image_sql)
        conn.commit()
        game_image = curs.fetchone()

        price = 40

        user_avg_rating_sql = f"SELECT AVG(rating) FROM rates WHERE vid={gameId[0]};"#Get average rating of game.
        curs.execute(user_avg_rating_sql)
        conn.commit()
        user_avg_rating = curs.fetchone()


        developer_list_sql = f"SELECT sname FROM development INNER JOIN studio ON development.sid = studio.sid WHERE vid={gameId[0]};"
        curs.execute(developer_list_sql)
        conn.commit()
        developer_list_raw = curs.fetchall()
        developer_list = []
        for tup in developer_list_raw:
            developer_list.append(tup[0])

        publisher_list_sql = f"SELECT sname FROM publishing INNER JOIN studio ON publishing.sid = studio.sid WHERE vid={gameId[0]};"
        curs.execute(publisher_list_sql)
        conn.commit()
        publisher_list_raw = curs.fetchall()
        publisher_list = []
        for tup in publisher_list_raw:
            publisher_list.append(tup[0])
        #Get esrb rating
        game_esrb_rating_sql = f"SELECT esrb_rating FROM video_game WHERE vid={gameId[0]};"
        curs.execute(game_esrb_rating_sql)
        conn.commit()
        game_esrb_rating = curs.fetchone()


        #Get playtime
        user_playtime_sql = f"SELECT starttime, endtime FROM gameplay WHERE vid={gameId[0]} AND uid={LOGGED_IN_USER_ID};"
        curs.execute(user_playtime_sql)
        conn.commit()
        user_playtime = curs.fetchall()


        platform_list_sql = f"SELECT pname FROM platform INNER JOIN game_platform ON game_platform.pid = platform.pid WHERE vid={gameId[0]};"
        curs.execute(platform_list_sql)
        conn.commit()
        platform_list_raw = curs.fetchall()
        platform_list = []
        for tup in platform_list_raw:
            platform_list.append(tup[0])

        game_dict = {
            "vid": str(gameId[0]),
            "name": game_name[0],
            "description": game_desc[0],
            "price": price,
            "banner": game_image[0],
            "platforms": platform_list,
            "developers": developer_list,
            "publishers": publisher_list,
            "gameplay": user_playtime,
            "esrb_rating": game_esrb_rating[0],
            "rating": user_avg_rating[0]
        }

        games_results.append(game_dict)

    #List of dictionaries of:
        #(name, [platforms], [developers], publisher, user's playtime, esrb rating, user average rating.)
    return games_results, 200


#Test all of the following features.

@app.route("/api/videogame/<uid>/followers", methods = ['GET'])
@cross_origin(origins="*")
def getTotalFollowers(uid):#Get all followers of a uid.
    #Gets the count of the followers of a particular user
    #fid:uid of the user following someone with a uid
    #SQL statement works.
    sql_get_total_followers = "SELECT count(fid) FROM friends WHERE uid = %s"
    curs.execute(sql_get_total_followers, uid)
    conn.commit()
    followers_num = curs.fetchone()#Should just return a tuple
    followers_dict = {
        "followers" :  followers_num[0]
    }

    return followers_dict, 200

@app.route("/api/videogame/<uid>/following", methods = ['GET'])
@cross_origin(origins="*")
def getTotalFollowed(uid):#Get all people a person follows.
    #fid:uid of the user following someone with a uid
    #SQL statement works.
    sql_get_total_followed = "SELECT count(uid) FROM friends WHERE fid = %s"
    curs.execute(sql_get_total_followed, uid)
    conn.commit()
    followed_num = curs.fetchone()#Should just return a tuple
    followed_dict = {
        "followed" :  followed_num[0]
    }

    return followedDict, 200

@app.route("/api/videogame/<uid>/collectionNumber", methods = ['GET'])
@cross_origin(origins="*")
def getUserCollectionNumber(uid):#Get all people a person follows.
    #fid:uid of the user following someone with a uid
    #SQL statement works.
    sql_get_total_collections = "SELECT count(cid) from collections_made WHERE uid = %s"
    curs.execute(sql_get_total_collections, uid)
    conn.commit()
    collection_num = curs.fetchone()#Should just return a tuple containing number.
    followed_dict = {
        "totalCollections" :  collection_num[0]
    }

    return followed_dict, 200

#Currently untested.
#Do this by ratings.
#Add in price.
@app.route("/api/videogame/<uid>/topTenGames", methods = ['GET'])
@cross_origin(origins="*")
def getUserTopTenGames(uid):
    sql_get_vid_ratings_pair = "SELECT vid, rating FROM rates WHERE uid = %s ORDER BY rating DESC LIMIT 10"
    curs.execute(sql_get_vid_ratings_pair, uid)
    conn.commit()
    top_ten_data = []
    vid_rating_data = curs.fetchall()#From the top to the tenth top game.
    for vid_pair in vid_rating_data:

        game_name_sql = f"SELECT title FROM video_game WHERE vid={vid_pair[0]};"
        curs.execute(game_name_sql)
        conn.commit()
        game_name = curs.fetchone()

        game_desc_sql = f"SELECT description FROM video_game WHERE vid={vid_pair[0]};"
        curs.execute(game_desc_sql)
        conn.commit()
        game_desc = curs.fetchone()

        game_image_sql = f"SELECT image FROM video_game WHERE vid={vid_pair[0]};"
        curs.execute(game_image_sql)
        conn.commit()
        game_image = curs.fetchone()

        user_avg_rating_sql = f"SELECT AVG(rating) FROM rates WHERE vid={vid_pair[0]};"#Get average rating of game.
        curs.execute(user_avg_rating_sql)
        conn.commit()
        user_avg_rating = curs.fetchone()


        developer_list_sql = f"SELECT sname FROM development INNER JOIN studio ON development.sid = studio.sid WHERE vid={vid_pair[0]};"
        curs.execute(developer_list_sql)
        conn.commit()
        developer_list_raw = curs.fetchall()
        developer_list = []
        for tup in developer_list_raw:
            developer_list.append(tup[0])

        publisher_list_sql = f"SELECT sname FROM publishing INNER JOIN studio ON publishing.sid = studio.sid WHERE vid={vid_pair[0]};"
        curs.execute(publisher_list_sql)
        conn.commit()
        publisher_list_raw = curs.fetchall()
        publisher_list = []
        for tup in publisher_list_raw:
            publisher_list.append(tup[0])
        #Get esrb rating
        game_esrb_rating_sql = f"SELECT esrb_rating FROM video_game WHERE vid={vid_pair[0]};"
        curs.execute(game_esrb_rating_sql)
        conn.commit()
        game_esrb_rating = curs.fetchone()


        #Get playtime
        user_playtime_sql = f"SELECT starttime, endtime FROM gameplay WHERE vid={vid_pair[0]} AND uid={LOGGED_IN_USER_ID};"
        curs.execute(user_playtime_sql)
        conn.commit()
        user_playtime = curs.fetchall()


        platform_and_price_list_sql = f"SELECT pname, price FROM platform INNER JOIN game_platform ON game_platform.pid = platform.pid WHERE vid={vid_pair[0]};"
        curs.execute(platform_and_price_list_sql)
        conn.commit()
        platform_and_price_list = curs.fetchall()

        top_ten_dict = {
            "vid" : vid_pair[0],
            "user_rating" : vid_pair[1],
            "name": game_name[0],
            "description": game_desc[0],
            "banner": game_image[0],
            "platforms": platform_and_price_list,
            "developers": developer_list,
            "publishers": publisher_list,
            "gameplay": user_playtime,
            "esrb_rating": game_esrb_rating[0],
            "rating": user_avg_rating[0]
        }
        top_ten_data.append(top_ten_dict)
    return top_ten_data, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)