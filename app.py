from flask import Flask
from flask_cors import CORS
from db import mysql
import config

app = Flask(__name__)
CORS(app)

# DB config
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql.init_app(app)

@app.route('/')
def home():
    return {"message": "Backend running"}

if __name__ == '__main__':
    app.run(debug=True)