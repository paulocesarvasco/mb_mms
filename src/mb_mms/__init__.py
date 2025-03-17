from flask import Flask
from dotenv import load_dotenv

from mb_mms.api.routes import currency_bp
from mb_mms.services.data import db

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.register_blueprint(currency_bp)

    db.init_app(app)

    return app
