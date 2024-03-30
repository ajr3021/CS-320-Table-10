from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import datetime
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from sshtunnel import SSHTunnelForwarder
#Finished all of the first draft code.
    #Need to test all methods.
        #Test if the routes and param structure works correctly
        #Test the individual sql statements.

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
    sql = "SELECT * FROM video_game WHERE vid=%s;"

    curs.execute(sql, (vid,))
    result = curs.fetchall()#This should always be of size one. Otherwise database has an issue.
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

    #Sort alphabetically and release date-wise ascending
    #Tables used:
        #video_game (name, esrb rating)
        #game_platform (needed to get price, release_date)
        #Gameplay (for that of user)
        #publishing (for publishers)
        #development (needed to get all developers of a game)
        #rates (needed to get average of all user ratings)
    #Development and publishing are BOTH going to be arrays. I could get them in a separate sql query and return a new list of resulting tuples(?)
    subQuery
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
    curs.execute(sql)
    conn.commit()
    game_list = curs.fetchall()#This should fetch tuples of title and vid
    for gameId in game_list:

        game_name_sql = f"SELECT title FROM video_game WHERE vid={gameId[0][0]};"
        curs.execute(game_name_sql)
        conn.commit()
        game_name = curs.fetchone()

        user_avg_rating_sql = f"SELECT AVG(rating) FROM rates WHERE vid={gameId[0][0]};"#Get average rating of game.
        curs.execute(user_avg_rating_sql)
        conn.commit()
        user_avg_rating = curs.fetchone()

        
        developer_list_sql = f"SELECT sname FROM development INNER JOIN studio ON development.vid = studio.vid WHERE vid={gameId[0][0]};"
        curs.execute(developer_list_sql)
        conn.commit()
        developer_list = curs.fetchall()


        publisher_list_sql = f"SELECT sname FROM publishing INNER JOIN studio ON development.vid = studio.vid WHERE vid={gameId[0][0]};"
        curs.execute(publisher_list_sql)
        conn.commit()
        publisher_list = curs.fetchall()


        #Get esrb rating
        game_esrb_rating_sql = f"SELECT esrb_rating FROM video_game WHERE vid={gameId[0][0]};"
        curs.execute(game_esrb_rating_sql)
        conn.commit()
        game_esrb_rating = curs.fetchall()


        #Get playtime
        user_playtime_sql = f"SELECT starttime, endtime FROM gameplay WHERE vid={gameId[0][0]} AND uid={uid};" 
        curs.execute(user_playtime_sql)
        conn.commit()
        user_playtime = curs.fetchall()


        platform_list_sql = f"SELECT pname FROM platform INNER JOIN game_platform ON game_platform.pid = platform.pid WHERE vid={gameId[0]};"
        curs.execute(platform_list_sql)
        conn.commit()
        platform_list = curs.fetchall()


        game_dict = {
            "title": game_name[0],
            "platforms": platform_list,
            "developers": developer_list,
            "publishers": publisher_list,
            "startTime": user_playtime[0][0],
            "endTime": user_playtime[0][1]
            "esrb_rating": game_esrb_rating[0],
            "userRating": user_average_rating[0]
        }

        games_results.append(game_dict)

    #List of dictionaries of:
        #(name, [platforms], [developers], publisher, user's playtime, esrb rating, user average rating.)
    return games_results, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)