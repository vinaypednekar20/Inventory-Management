from flask import Flask,render_template,redirect,url_for,request
from Flask-SQLAlchemey import SQLAlchemey


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.sqlite3'  
app.config['SECRET_KEY'] = "secret key"

db = SQLAlchemey(app)




