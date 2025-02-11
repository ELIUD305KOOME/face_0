import os
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename
from models import db, Service

# Define Blueprint
services_bp = Blueprint('services', __name__)
api = Api(services_bp)

# Request parsers
service_parser = reqparse.RequestParser()
service_parser.add_argument('name', type=str, required=True, help="Name is required")
service_parser.add_argument('description', type=str)
service_parser.add_argument('price', type=float, required=True)
service_parser.add_argument('category_name', type=str, required=True)
service_parser.add_argument('subcategory_name', type=str, required=True)
service_parser.add_argument('before_service_image', type=str)  # Used for URL-based images
service_parser.add_argument('after_service_image', type=str) # Used for URL-

# Helper function for saving uploaded files
def save_uploaded_file(file):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

def save_after_file(file):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/after')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

# Resources
class ServiceListResource(Resource):
    def get(self):
        services = Service.query.all()
        return [service.to_dict() for service in services], 200

    def post(self):
        args = service_parser.parse_args()
        uploaded_file = request.files.get('file')  # Check if a file is uploaded
        before_service_image = None
        after_service_image = None

        if uploaded_file:
            before_service_image = save_uploaded_file(uploaded_file)
        elif args.get('before_service_image'):
            before_service_image = args.get('before_service_image')  # Use provided URL

        if uploaded_file:
            after_service_image = save_after_file(uploaded_file)
        elif args.get('after_service_image'):
            after_service_image = args.get('after_service_image')  # Use provided URL
        


        service = Service(
            name=args['name'],
            description=args.get('description'),
            price=args['price'],
            category_name=args['category_name'],
            subcategory_name=args['subcategory_name'],
            before_service_image=before_service_image,
            after_service_image=after_service_image  
        )
        db.session.add(service)
        db.session.commit()
        return service.to_dict(), 201

class ServiceResource(Resource):
    def get(self, id):
        service = Service.query.get_or_404(id)
        return service.to_dict(), 200

    def put(self, id):
        service = Service.query.get_or_404(id)
        args = service_parser.parse_args()
        uploaded_file = request.files.get('file')
        before_service_image = service.before_service_image  # Keep existing value if no new file or URL provided
        after_service_image = service.after_service_image  # Keep existing value if no new file or URL provided

        if uploaded_file:
            before_service_image = save_uploaded_file(uploaded_file)
        elif args.get('before_service_image'):
            before_service_image = args.get('before_service_image')# Use provided URL

        if uploaded_file:
            after_service_image = save_after_file(uploaded_file)
        elif args.get('after_service_image'):
            after_service_image = args.get('after_service_image')  # Use provided URL

        

        

        service.name = args['name']
        service.description = args.get('description')
        service.price = args['price']
        service.category_name = args['category_name']
        service.subcategory_name = args['subcategory_name']
        service.before_service_image = before_service_image
        service.after_service_image = after_service_image
        db.session.commit()
        return service.to_dict(), 200

    def delete(self, id):
        service = Service.query.get_or_404(id)
        db.session.delete(service)
        db.session.commit()
        return '', 204

# Add Resources to the API
api.add_resource(ServiceListResource, '/services')
api.add_resource(ServiceResource, '/services/<int:id>')
