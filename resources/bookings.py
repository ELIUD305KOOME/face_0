from flask import Blueprint, request, jsonify, redirect
from flask_restful import Api, Resource
from models import db, Product, Service,Booking

# Define Blueprint
clicks_bp = Blueprint('clicks', __name__)
api = Api(clicks_bp)

# Click Tracker for Product Booking
# @limiter.exempt
class ProductClickResource(Resource):
    def post(self, product_id):
        # Fetch product by ID
        product = Product.query.get_or_404(product_id)
        product.clicks += 1
        db.session.commit()

        # Fetch customer information from the request
        name = request.json.get('name')
        phone = request.json.get('phone')
        message = request.json.get('message')

        # Check if all required fields are provided
        if not name or not phone or not message:
            return jsonify({"error": "Missing required information. Name, phone, and message are required."}), 400

        # Store booking details in the database
        booking = Booking(product_id=product.id, name=name, phone=phone, message=message)
        db.session.add(booking)
        db.session.commit()

        # Construct the WhatsApp URL including the product details and customer information
        whatsapp_url = f"https://wa.me/+254722669912?text=I%20am%20interested%20in%20the%20product%20'{product.name}'%20priced%20at%20{product.price}%0AName:%20{name}%0APhone:%20{phone}%0AMessage:%20{message}"

        return jsonify({"whatsapp_url": whatsapp_url, "message": "Booking details stored successfully."})


# @limiter.exempt
class AllProductClicksResource(Resource):
    def get(self):
        products = Product.query.all()
        product_clicks = [{"product_id": product.id, "name": product.name, "clicks": product.clicks} for product in products]
        return {"products": product_clicks}, 200

# Click Tracker for Service Booking
# @limiter.exempt
class ServiceClickResource(Resource):
    def post(self, service_id):
        # Fetch service by ID
        service = Service.query.get_or_404(service_id)
        service.clicks += 1
        db.session.commit()

        # Fetch customer information from the request
        name = request.json.get('name')
        phone = request.json.get('phone')
        message = request.json.get('message')

        # Check if all required fields are provided
        if not name or not phone or not message:
            return jsonify({"error": "Missing required information. Name, phone, and message are required."}), 400

        # Store booking details in the database
        booking = Booking(service_id=service.id, name=name, phone=phone, message=message)
        db.session.add(booking)
        db.session.commit()

        # Construct the WhatsApp URL including the service details and customer information
        whatsapp_url = f"https://wa.me/+254722669912?text=I%20am%20interested%20in%20the%20service%20'{service.name}'%20priced%20at%20{service.price}%0AName:%20{name}%0APhone:%20{phone}%0AMessage:%20{message}"

        return jsonify({"whatsapp_url": whatsapp_url, "message": "Booking details stored successfully."})


# @limiter.exempt
class AllServiceClicksResource(Resource):
    def get(self):
        services = Service.query.all()
        service_clicks = [{"service_id": service.id, "name": service.name, "clicks": service.clicks} for service in services]
        return {"services": service_clicks}, 200

# API for Total Clicks
class TotalClicksResource(Resource):
    def get(self):
        total_product_clicks = db.session.query(db.func.sum(Product.clicks)).scalar() or 0
        total_service_clicks = db.session.query(db.func.sum(Service.clicks)).scalar() or 0
        return {
            "total_product_clicks": total_product_clicks,
            "total_service_clicks": total_service_clicks,
            "total_clicks": total_product_clicks + total_service_clicks
        }, 200

# Add Resources to the API
api.add_resource(ProductClickResource, '/products/<int:product_id>/clicks')
api.add_resource(AllProductClicksResource, '/products/clicks')
api.add_resource(ServiceClickResource, '/services/<int:service_id>/clicks')
api.add_resource(AllServiceClicksResource, '/services/clicks')
api.add_resource(TotalClicksResource, '/total-clicks')
