from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from datetime import timedelta
from model import db
from routes.auth import auth_bp
from routes.stats import stats_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'zencura-hospital-secret-key-2026-secure'
app.config['JWT_SECRET_KEY'] = 'zencura-jwt-secret-key-2026-very-secure'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
