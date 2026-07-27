from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from config import Config

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins=os.getenv('CORS_ORIGIN', 'http://localhost:3000'))

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    return {'message': 'Portfolio endpoint - not implemented yet'}, 501

@app.route('/api/portfolio/items', methods=['GET'])
def get_portfolio_items():
    return {'message': 'Portfolio items endpoint - not implemented yet'}, 501

if __name__ == '__main__':
    debug = app.config['DEBUG']
    port = int(os.getenv('API_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
