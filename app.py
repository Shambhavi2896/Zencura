from flask import Flask
from model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hospital-secret-key-2026'

db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
