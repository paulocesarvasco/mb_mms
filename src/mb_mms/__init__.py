from flask import Flask
from mb_mms.api.routes import currency_bp

def create_app():

    app = Flask(__name__)

    app.register_blueprint(currency_bp)

    return app
