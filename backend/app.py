import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import config
from openapi import api
from routes.portfolio import portfolio_bp
from routes.prices import prices_bp
from routes.transactions import transactions_bp

load_dotenv()

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

logging.basicConfig(
    level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
    format='[%(levelname)-5s] %(name)s: %(message)s',
)

CORS(app, origins=os.getenv('CORS_ORIGIN', 'http://localhost:3000'))

app.register_blueprint(portfolio_bp)
app.register_blueprint(prices_bp)
app.register_blueprint(transactions_bp)
api.register(app)  # UI served at /apidocs/swagger


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    debug = app.config['DEBUG']
    port = int(os.getenv('API_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug, reloader_type='stat')
