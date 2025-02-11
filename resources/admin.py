from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_talisman import Talisman
import datetime
from flask import Flask


# Initialize the Flask app
app = Flask(__name__)

# Initialize Flask-Limiter for rate limiting
# limiter = Limiter(key_func=get_remote_address,app=app,   default_limits=["200 per day", "50 per hour"])

# # Secure HTTP headers using Flask-Talisman
# talisman = Talisman()

# Define Blueprints
auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)

# Request parser for admin creation
admin_parser = reqparse.RequestParser()
admin_parser.add_argument('name', type=str, required=True, help="Name is required")
admin_parser.add_argument('email', type=str, required=True, help="Email is required")
admin_parser.add_argument('password', type=str, required=True, help="Password is required")

# Helper function: lock accounts temporarily after failed attempts
FAILED_ATTEMPTS = {}
LOCKOUT_DURATION = datetime.timedelta(minutes=15)
MAX_FAILED_ATTEMPTS = 5


def is_account_locked(email):
    attempt_info = FAILED_ATTEMPTS.get(email)
    if not attempt_info:
        return False
    failed_attempts, last_failed_time = attempt_info
    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        if datetime.datetime.now() - last_failed_time < LOCKOUT_DURATION:
            return True
        else:
            # Reset failed attempts after lockout duration
            FAILED_ATTEMPTS.pop(email)
    return False


def record_failed_attempt(email):
    if email in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[email] = (FAILED_ATTEMPTS[email][0] + 1, datetime.datetime.now())
    else:
        FAILED_ATTEMPTS[email] = (1, datetime.datetime.now())


# Admin Login Resource
class AdminLoginResource(Resource):
    # decorators = [limiter.limit("5 per minute")]

    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Check if account is locked
        if is_account_locked(email):
            return {"message": "Account is temporarily locked due to multiple failed attempts. Try again later."}, 403

        admin = Admin.query.filter_by(email=email).first()
        if not admin or not check_password_hash(admin.password_hash, password):
            record_failed_attempt(email)
            return {"message": "Invalid credentials"}, 401

        # Reset failed attempts on successful login
        if email in FAILED_ATTEMPTS:
            FAILED_ATTEMPTS.pop(email)

        # Generate JWT tokens
        access_token = create_access_token(identity={"id": admin.id, "email": admin.email}, expires_delta=datetime.timedelta(minutes=15))
        refresh_token = create_refresh_token(identity={"id": admin.id, "email": admin.email})
        return {"access_token": access_token, "refresh_token": refresh_token}, 200


# Admin Register Resource
class AdminRegisterResource(Resource):
    def post(self):
        args = admin_parser.parse_args()
        hashed_password = generate_password_hash(args['password'], method='argon2')  # Using Argon2 for password hashing

        admin = Admin(
            name=args['name'],
            email=args['email'],
            password_hash=hashed_password,
        )
        db.session.add(admin)
        db.session.commit()
        return admin.to_dict(), 201


# Token Refresh Endpoint
class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, expires_delta=datetime.timedelta(minutes=15))
        return {"access_token": new_access_token}, 200


# Add resources to their respective APIs
auth_api.add_resource(AdminLoginResource, '/login')
auth_api.add_resource(AdminRegisterResource, '/register')
auth_api.add_resource(TokenRefreshResource, '/refresh')

# Add rate limiting and security headers
# limiter.init_app(auth_bp)
# talisman.init_app(auth_bp)
