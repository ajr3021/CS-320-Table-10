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

@app.route("/api/videogame/")
@cross_origin(origins="*")
def get_random_videogame():
    sql = f"SELECT * FROM video_game ORDER BY RAND() LIMIT 1;"

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

@app.route("/api/collection/<cid>")
@cross_origin(origins="*")
def update_collection_name(cid, name):
    sql = f"UPDATE collection SET CName = {name} WHERE cid={cid};"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    return result

@app.route("/api/collection/<cid>/<vid>")
@cross_origin(origins="*")
def insert_videogame_into_collection(cid, vid):
    sql = f"INSERT INTO CollectionHas (CID, VID) VALUES ({cid}, {vid});"

    curs.execute(sql)
    result = curs.fetchall()
    conn.commit()

    return result

@app.route("/api/collection/<cid>/<vid>", methods=['DELETE'])
@cross_origin(origins="*")
def delete_videogame_from_collection(cid, vid):
    sql = f"DELETE FROM CollectionHas WHERE CID = {cid} and VID = {vid};"

    curs.execute(sql)
    conn.commit()

    return {}, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
