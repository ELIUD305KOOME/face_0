import os
from flask import Blueprint, request, current_app, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from models import db, Product

# Define Blueprint
products_bp = Blueprint('products', __name__)
api = Api(products_bp)




# Request parsers
product_parser = reqparse.RequestParser()
product_parser.add_argument('name', type=str, required=True, help="Name is required")
product_parser.add_argument('category_name', type=str, required=True)
product_parser.add_argument('subcategory_name', type=str, required=True)
product_parser.add_argument('description', type=str, required=True)
product_parser.add_argument('price', type=float, required=True)
product_parser.add_argument('image_url', type=str)  # For URL-based images
# '''uploads/products/files'''

# Helper function for saving uploaded files
def save_uploaded_files(file):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/products')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path


# Resources
class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return [product.to_dict() for product in products], 200
    # @token_required
    def post(self):
        args = product_parser.parse_args()
        uploaded_file = request.files.get('file')  # Check for uploaded file
        image_url = None

        if uploaded_file:
            image_url = save_uploaded_files(uploaded_file)  # Save file and get path
        elif args.get('image_url'):
            image_url = args.get('image_url')  # Use provided URL

        # # Check for duplicate product name
        # existing_product = Product.query.filter_by(name=args['name']).first()
        # if existing_product:
        #     return jsonify({"error": "Product name already exists"}), 400

        product = Product(
            name=args['name'],
            category_name=args['category_name'],
            subcategory_name=args['subcategory_name'],
            description=args['description'],
            price=args['price'],
            image_url=image_url,
        )

        try:
            db.session.add(product)
            db.session.commit()
            return product.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Failed to create product due to a database constraint"}), 400

class ProductResource(Resource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product.to_dict(), 200
    
    def put(self, id):
        product = Product.query.get_or_404(id)
        args = product_parser.parse_args()
        uploaded_file = request.files.get('file')
        image_url = product.image_url  # Keep existing value unless a new one is provided

        if uploaded_file:
            image_url = save_uploaded_files(uploaded_file)
        elif args.get('image_url'):
            image_url = args.get('image_url')

        # Check for duplicate product name (excluding current product)
        if Product.query.filter(Product.id != id, Product.name == args['name']).first():
            return jsonify({"error": "Product name already exists"}), 400

        product.name = args['name']
        product.category_name = args['category_name']
        product.subcategory_name = args['subcategory_name']
        product.description = args['description']
        product.price = args['price']
        product.image_url = image_url

        try:
            db.session.commit()
            return product.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Failed to update product due to a database constraint"}), 400

    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return '', 204

# Add Resources to the API
api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:id>')
