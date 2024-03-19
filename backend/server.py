from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#index route
@app.route("/message")
@cross_origin(origins="*")
def index():
    import psycopg2
    from sshtunnel import SSHTunnelForwarder

    username = ""
    password = ""
    dbName = "p320_10"

    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=('127.0.0.1', 5432)) as server:
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

            sql = "SELECT * FROM collection;"

            curs.execute(sql)
            result = curs.fetchall() 

            print(result)

            conn.commit()

            conn.close()

            return {"message": str(result)}
    except Exception as e:
        print("Connection failed")
        print(e)
        return {"message": "Exception"}
        
    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)