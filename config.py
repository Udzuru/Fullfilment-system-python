
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.secret_key = "Anthony_get_Sick"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///goods_management.db"

db = SQLAlchemy(app)

