from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#index route
@app.route("/message")
@cross_origin(origins="*")
def index():
    return {"message": "hello"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)