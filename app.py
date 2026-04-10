from pathlib import Path

from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from model import db
from backend.core.config import get_config
from backend.routes.auth import auth_bp
from backend.routes.stats import stats_bp
from backend.routes.admin import admin_bp
from backend.routes.doctor import doctor_bp
from backend.routes.patient import patient_bp
from backend.routes.appointment import appointment_bp
from backend.routes.search import search_bp
from backend.routes.payment import payment_bp
from backend.routes.reports import reports_bp
from backend.routes.pdf_export import pdf_bp
from backend.routes.export import export_bp


def create_app(config=None):
    base_dir = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        static_folder=str(base_dir / 'frontend' / 'static'),
        template_folder=str(base_dir / 'frontend' / 'templates'),
        instance_path=str(base_dir / 'backend' / 'instance'),
        instance_relative_config=True,
    )

    if config is None:
        config = get_config()
    app.config.from_object(config)

    db.init_app(app)
    JWTManager(app)
    Mail(app)

    from backend.core.cache import init_cache_with_fallback

    init_cache_with_fallback(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(export_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

