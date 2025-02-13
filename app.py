from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models import db
from resources.admin import auth_bp
from resources.bookings import clicks_bp
from resources.products import products_bp
from resources.services import services_bp
from resources.booking import booking_bp
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from whitenoise import WhiteNoise
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the app
CORS(app, origins=['https://solomonbeautyservices.vercel.app'])

# Flask app configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')  # Use DATABASE_URL from environment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sominolies_user:gOn4c7PIFLEgOFnBLOMNCgBi4w0C1Yto@dpg-culjv823esus73cvglrg-a.oregon-postgres.render.com/sominolies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')  # Use JWT_SECRET_KEY from environment
app.config['UPLOAD_FOLDER'] = 'uploads/products'
app.config['UPLOAD_FOLDER_AFTER'] = 'uploads/after'
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2000000 per day", "50000 per hour"],  # Global rate limits
)

# Initialize Flask-Talisman for security headers
talisman = Talisman(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(clicks_bp)
app.register_blueprint(products_bp)
app.register_blueprint(services_bp)
app.register_blueprint(booking_bp)

# Create API instance
api = Api(app)

@app.route('/')
def hello():
    return jsonify(message="Hello from Flask! Welcome to solo beauty services!")

# Run locally
if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
